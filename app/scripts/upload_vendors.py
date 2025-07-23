import csv
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Vendor  # make sure path is correct
from app.db.base import Base    
from app.config import settings  # for metadata.create_all if needed
import os
DATABASE_URL = settings.database_url
CSV_FILE = "bewhoop_schema_mock.csv"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def upload_vendors():
    async with AsyncSessionLocal() as session:
        try:
            print(f" Loading vendors from: {CSV_FILE}")
            with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                cleaned_fieldnames = [field.strip() for field in reader.fieldnames]
                print(" Cleaned CSV Headers:", cleaned_fieldnames)

                for row in reader:
                    row = {k.strip(): v.strip() for k, v in row.items()}
                    vendor = Vendor(
                        vendor_name=row.get("Vendor Name", ""),
                        contact_email=row.get("Contact Email", ""),
                        notes=row.get("Notes", ""),
                        phone_number=row.get("Phone Number", ""),
                        status=row.get("Status", "Not started"),
                        vendor_city=row.get("Vendor City", ""),
                        vendor_services=row.get("Vendor Services", ""),
                        vendor_type=row.get("Vendor Type", ""),
                        instagram_link=row.get("Instagram link", ""),
                        created_by=row.get("Created by", "")
                    )
                    session.add(vendor)
                await session.commit()
                print(" Vendors uploaded successfully!")
        except Exception as e:
            print(f"Error uploading vendors: {e}")

if __name__ == "__main__":
    asyncio.run(upload_vendors())
