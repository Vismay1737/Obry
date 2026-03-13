from fastapi import APIRouter, HTTPException, BackgroundTasks
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

        # Define all tool tasks using the shared connection
        tasks = [
            run_and_save("nmap", ScannerService.run_nmap(target, conn=conn)),
            run_and_save("whatweb", ScannerService.run_whatweb(target, conn=conn)),
            run_and_save("httpx", ScannerService.run_httpx(target, conn=conn)),
            run_and_save("subfinder", ScannerService.run_subfinder(target, conn=conn)),
            run_and_save("amass", ScannerService.run_amass(target, conn=conn)),
            run_and_save("gau", ScannerService.run_gau(target, conn=conn)),
            run_and_save("nikto", ScannerService.run_nikto(target, conn=conn)),
            run_and_save("nuclei", ScannerService.run_nuclei(target, conn=conn)),
            run_and_save("katana", ScannerService.run_katana(target, conn=conn)),
        ]

        # Run all tools concurrently
        await asyncio.gather(*tasks)

        # STAGE: AI Analysis
        ai_analysis = await AIService.analyze_results(target, results)

        # Baseline heuristic parsing
        score = 100
        detected_vulns = []
        
        if results.get("nmap") and "open" in str(results["nmap"]).lower():
            score -= 10
            detected_vulns.append({
                "title": "Open Network Services",
                "severity": "medium",
                "description": "Port scanning identified exposed services on the target machine.",
                "recommendation": "Close unused ports and implement a strict firewall policy."
            })
        
        if results.get("nikto") and "vulnerabilities" in str(results["nikto"]).lower():
            score -= 20
            detected_vulns.append({
                "title": "Web Server Vulnerabilities",
                "severity": "high",
                "description": "Nikto scan identified potential misconfigurations or outdated web software.",
                "recommendation": "Update web server software and follow OWASP hardening guides."
            })

        if results.get("nuclei") and any(x in str(results["nuclei"]).lower() for x in ["[high]", "[critical]", "[medium]"]):
            score -= 30
            detected_vulns.append({
                "title": "Advanced Exploit Detected",
                "severity": "high",
                "description": "Nuclei advanced vulnerability scanner identified significant security flaws.",
                "recommendation": "Review Nuclei logs and apply patches for identified CVEs immediately."
            })

        from datetime import datetime, timezone
        # Final update
        await db["scans"].update_one(
            {"_id": ObjectId(scan_id)},
            {
                "$set": {
                    "status": "completed",
                    "raw_output": results,
                    "ai_analysis": ai_analysis,
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
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    new_scan = ScanResult(target=request.target, status="running")
    scan_dict = new_scan.model_dump(by_alias=True, exclude_none=True)

    result = await db["scans"].insert_one(scan_dict)
    scan_id = result.inserted_id
    new_scan.id = str(scan_id)

    background_tasks.add_task(background_scan_task, request.target, str(scan_id))
    return new_scan


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
