from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio
from bson import ObjectId
from models.scan import ScanRequest, ScanResult
from services.scanner import ScannerService
from services.ai import AIService
from db.database import get_db
import traceback
import asyncssh
from core.config import settings

router = APIRouter()

active_connections: Dict[str, List[WebSocket]] = {}

async def broadcast_log(scan_id: str, tool: str, log_line: str):
    if scan_id in active_connections:
        for ws in active_connections[scan_id]:
            try:
                await ws.send_json({"tool": tool, "log": log_line})
            except Exception:
                pass

import re
import ipaddress

def is_valid_target(target: str) -> bool:
    target = target.strip()
    if not target or len(target) > 255:
        return False
        
    # Remove protocol if present for validation
    if target.startswith("http://") or target.startswith("https://"):
        target = target.split("://")[1].split("/")[0]

    # Prevent command injection metacharacters immediately
    if any(char in target for char in [";", "|", "&", "$", ">", "<", "`", "\\", "!", "\n", "\r", " ", "\t"]):
        return False

    # Check if target is an IP address
    try:
        ip = ipaddress.ip_address(target)
        # Block SSRF & Internal scanning
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            return False
        return True # Valid public IP
    except ValueError:
        pass # It's a domain name, not an IP

    # Validate Domain format
    domain_regex = re.compile(
        r"^(?:[a-zA-Z0-9]"
        r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
        r"[a-zA-Z]{2,10}$"
    )
    if not domain_regex.match(target):
        return False

    return True


async def background_scan_task(target: str, scan_id: str):
    db = get_db()
    results = {}
    
    # helper to run a tool and save to results
    async def run_and_save(tool_name: str, coro):
        try:
            output = await coro
            results[tool_name] = output
        except Exception as e:
            results[tool_name] = f"Error: {str(e)}"
            print(f"Tool {tool_name} failed: {traceback.format_exc()}")
        
        # Save partial results after each tool finishes
        await db["scans"].update_one(
            {"_id": ObjectId(scan_id)},
            {"$set": {"raw_output": results}}
        )

    conn = None
    try:
        # Establish a single persistent connection if using remote Kali
        if settings.KALI_HOST:
            try:
                conn = await asyncssh.connect(
                    settings.KALI_HOST, 
                    port=settings.SSH_PORT, 
                    username=settings.KALI_USER, 
                    password=settings.KALI_PASSWORD, 
                    known_hosts=None
                )
            except Exception as e:
                print(f"Failed to establish persistent SSH: {e}")

        # Define a factory to generate callbacks for each specific tool
        def get_cb(tool_name):
            async def cb(line):
                await broadcast_log(scan_id, tool_name, line)
            return cb

        # Define all tool tasks using the shared connection and live streaming websocket callback
        tasks = [
            run_and_save("nmap", ScannerService.run_nmap(target, conn=conn, callback=get_cb("nmap"))),
            run_and_save("whatweb", ScannerService.run_whatweb(target, conn=conn, callback=get_cb("whatweb"))),
            run_and_save("httpx", ScannerService.run_httpx(target, conn=conn, callback=get_cb("httpx"))),
            run_and_save("subfinder", ScannerService.run_subfinder(target, conn=conn, callback=get_cb("subfinder"))),
            run_and_save("amass", ScannerService.run_amass(target, conn=conn, callback=get_cb("amass"))),
            run_and_save("gau", ScannerService.run_gau(target, conn=conn, callback=get_cb("gau"))),
            run_and_save("nikto", ScannerService.run_nikto(target, conn=conn, callback=get_cb("nikto"))),
            run_and_save("nuclei", ScannerService.run_nuclei(target, conn=conn, callback=get_cb("nuclei"))),
            run_and_save("katana", ScannerService.run_katana(target, conn=conn, callback=get_cb("katana"))),
        ]

        # Run all tools concurrently
        await asyncio.gather(*tasks)

        # STAGE: AI Analysis (Structured & Autonomous Remediation)
        try:
            ai_analysis_dict = await AIService.analyze_results_dict(target, results)
            
            score = ai_analysis_dict.get("security_score", 100)
            ai_analysis_text = ai_analysis_dict.get("ai_analysis", "AI Analysis completed but no summary provided.")
            detected_vulns = ai_analysis_dict.get("vulnerabilities", [])
        except Exception as e:
            print(f"Failed to parse AI structured response: {e}")
            score = 100
            ai_analysis_text = "Analysis error occurred during JSON extraction."
            detected_vulns = []

        from datetime import datetime, timezone
        # Final update
        await db["scans"].update_one(
            {"_id": ObjectId(scan_id)},
            {
                "$set": {
                    "status": "completed",
                    "raw_output": results,
                    "ai_analysis": ai_analysis_text,
                    "security_score": max(0, score),
                    "vulnerabilities": detected_vulns,
                    "completed_at": datetime.now(timezone.utc)
                }
            }
        )
    except Exception as e:
        print(f"Error during background scan: {traceback.format_exc()}")
        await db["scans"].update_one(
            {"_id": ObjectId(scan_id)},
            {"$set": {"status": "failed", "raw_output": results, "error": str(e)}}
        )
    finally:
        if conn:
            conn.close()
            await conn.wait_closed()


@router.post("/scan", response_model=ScanResult)
async def trigger_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    try:
        db = get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not initialized")

        # STRICT TARGET VALIDATION (ANTI-SSRF & ANTI-COMMAND INJECTION)
        if not is_valid_target(request.target):
            raise HTTPException(
                status_code=400, 
                detail="Invalid target. Must be a valid public FQDN or IP address. Internal networks and bash metacharacters are strictly prohibited."
            )

        # Normalize target before scanning
        normalized_target = request.target.strip()
        if normalized_target.startswith("http://") or normalized_target.startswith("https://"):
            normalized_target = normalized_target.split("://")[1].split("/")[0]

        new_scan = ScanResult(target=normalized_target, status="running")
        scan_dict = new_scan.model_dump(by_alias=True, exclude_none=True)

        result = await db["scans"].insert_one(scan_dict)
        scan_id = result.inserted_id
        new_scan.id = str(scan_id)

        background_tasks.add_task(background_scan_task, normalized_target, str(scan_id))
        return new_scan
    except Exception as e:
        print("OMG ERROR IN TRIGGER_SCAN:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scans", response_model=list[ScanResult])
async def list_scans():
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    scans = await db["scans"].find().sort("created_at", -1).to_list(100)
    for scan in scans:
        scan["_id"] = str(scan["_id"])
    return scans


@router.get("/scans/{scan_id}", response_model=ScanResult)
async def get_scan(scan_id: str):
    from bson.errors import InvalidId
    db = get_db()
    try:
        obj_id = ObjectId(scan_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid scan ID format")

    scan = await db["scans"].find_one({"_id": obj_id})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    scan["_id"] = str(scan["_id"])
    return scan


@router.post("/consult")
async def consult_ai(request: dict):
    # request: {"scan_id": "...", "query": "..."}
    scan_id = request.get("scan_id")
    user_query = request.get("query")
    if not scan_id or not user_query:
        raise HTTPException(status_code=400, detail="Missing scan_id or query")
    
    from bson.errors import InvalidId
    try:
        obj_id = ObjectId(scan_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid scan ID format")

    db = get_db()
    scan = await db["scans"].find_one({"_id": obj_id})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    response = await AIService.consult(
        scan["target"], 
        scan.get("raw_output", {}), 
        user_query
    )
    return {"response": response}

@router.websocket("/ws/scan/{scan_id}")
async def websocket_scan_logs(websocket: WebSocket, scan_id: str):
    await websocket.accept()
    if scan_id not in active_connections:
        active_connections[scan_id] = []
    active_connections[scan_id].append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections[scan_id].remove(websocket)
        if not active_connections[scan_id]:
            active_connections.pop(scan_id, None)
