import asyncio
import httpx
from db.database import connect_to_mongo, get_db

async def main():
    print("Connecting to DB...")
    await connect_to_mongo()
    db = get_db()
    print(f"DB connected: {db}")

    print("Testing API...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.post("http://127.0.0.1:8000/api/scan", json={"target": "127.0.0.1"})
            print(r.status_code)
            print(r.text)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
