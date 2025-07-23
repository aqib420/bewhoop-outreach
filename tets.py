import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models import Vendor  # adjust paths if needed
from app.db.database import AsyncSessionLocal, get_db

# --- Direct AsyncSessionLocal test with relationship loading ---
async def test_direct_session_query():
    print("\n--- Testing AsyncSessionLocal with selectinload ---")
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Vendor).options(selectinload(Vendor.services))  # change this to real relation
            )
            vendors = result.scalars().all()
            for vendor in vendors:
                print(f"Vendor: {vendor.vendor_name}, Services: {vendor.services}")
        print("✅ Direct session query successful")
    except Exception as e:
        print(f"❌ Error in direct session query: {e}")

# --- Test get_db() dependency (simulates FastAPI yield) ---
async def test_get_db_yield():
    print("\n--- Testing get_db() dependency ---")
    try:
        db_gen = get_db()  # this is an async generator
        db = await anext(db_gen)  # equivalent to `async for db in get_db():`
        result = await db.execute(select(Vendor))
        vendors = result.scalars().all()
        print(f"Fetched {len(vendors)} vendors using get_db")
        await db_gen.aclose()
        print("✅ get_db dependency works correctly")
    except Exception as e:
        print(f"❌ Error in get_db dependency: {e}")

# --- Full runner ---
async def main():
    await test_direct_session_query()
    await test_get_db_yield()

if __name__ == "__main__":
    asyncio.run(main())
