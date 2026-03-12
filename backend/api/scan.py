from fastapi import APIRouter, HTTPException, BackgroundTasks
from bson import ObjectId
from models.scan import ScanRequest, ScanResult
from services.scanner import ScannerService
from db.database import get_db
import traceback

router = APIRouter()


async def background_scan_task(target: str, scan_id: str):
    db = get_db()
    try:
        # Run all Kali tools concurrently
        raw_results = await ScannerService.run_all_scans(target)

        # Save results directly — no AI step
        await db["scans"].update_one(
            {"_id": ObjectId(scan_id)},
            {
                "$set": {
                    "status": "completed",
                    "raw_output": raw_results,
                    "completed_at": __import__("datetime").datetime.utcnow()
                }
            }
        )
    except Exception as e:
        print(f"Error during background scan: {traceback.format_exc()}")
        await db["scans"].update_one(
            {"_id": ObjectId(scan_id)},
            {"$set": {"status": "failed", "raw_output": {"error": str(e)}}}
        )


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
    if not db:
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
