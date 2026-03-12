from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.scan import ScanRequest, ScanResult
from services.scanner import ScannerService
from services.ai import AIService
from db.database import get_db
import traceback

router = APIRouter()

async def background_scan_task(target: str, scan_id: str):
    db = get_db()
    try:
        # 1. Run raw scans
        raw_results = await ScannerService.run_all_scans(target)
        
        # 2. Update DB with raw results
        await db["scans"].update_one(
            {"_id": scan_id},
            {"$set": {"status": "analyzing", "raw_output": raw_results}}
        )

        # 3. Analyze with AI
        ai_result = await AIService.analyze_scan_results(raw_results)
        
        # 4. Save Final Results
        await db["scans"].update_one(
            {"_id": scan_id},
            {
                "$set": {
                    "status": "completed",
                    "ai_analysis": ai_result.get("ai_analysis"),
                    "vulnerabilities": ai_result.get("vulnerabilities", []),
                    "security_score": ai_result.get("security_score"),
                    "completed_at": __import__("datetime").datetime.utcnow()
                }
            }
        )
    except Exception as e:
        print(f"Error during background scan: {traceback.format_exc()}")
        await db["scans"].update_one(
            {"_id": scan_id},
            {"$set": {"status": "failed", "ai_analysis": f"Scan failed: {str(e)}"}}
        )

@router.post("/scan", response_model=ScanResult)
async def trigger_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    db = get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")

    # Create initial scan record
    new_scan = ScanResult(
        target=request.target,
        status="running"
    )
    scan_dict = new_scan.dict(by_alias=True, exclude_none=True)
    
    # insert into mongo
    result = await db["scans"].insert_one(scan_dict)
    scan_id = result.inserted_id
    new_scan.id = str(scan_id)

    # start background task
    background_tasks.add_task(background_scan_task, request.target, scan_id)

    return new_scan

@router.get("/scans", response_model=list[ScanResult])
async def list_scans():
    db = get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    scans = await db["scans"].find().sort("created_at", -1).to_list(100)
    # Convert ObjectId to str
    for scan in scans:
        scan["_id"] = str(scan["_id"])
    return scans

@router.get("/scans/{scan_id}", response_model=ScanResult)
async def get_scan(scan_id: str):
    from bson import ObjectId
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
