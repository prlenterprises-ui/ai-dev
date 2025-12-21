"""
Database migration: Add JSearch API response fields to job_applications table

Run with: python -m alembic upgrade head
Or manually: python migrate_add_jsearch_fields.py
"""

from sqlalchemy import text
from python.database import engine
import asyncio


async def migrate():
    """Add jsearch response fields to job_applications table."""
    
    async with engine.begin() as conn:
        print("Adding JSearch API response fields to job_applications table...")
        
        # Check which columns already exist
        result = await conn.execute(text("PRAGMA table_info(job_applications)"))
        columns = {row[1] for row in result}
        
        # Add columns if they don't exist
        if 'jsearch_search_response' not in columns:
            await conn.execute(text("""
                ALTER TABLE job_applications 
                ADD COLUMN jsearch_search_response TEXT
            """))
            print("  ✓ Added jsearch_search_response column")
        else:
            print("  - jsearch_search_response already exists")
        
        if 'jsearch_details_response' not in columns:
            await conn.execute(text("""
                ALTER TABLE job_applications 
                ADD COLUMN jsearch_details_response TEXT
            """))
            print("  ✓ Added jsearch_details_response column")
        else:
            print("  - jsearch_details_response already exists")
        
        if 'jsearch_salary_response' not in columns:
            await conn.execute(text("""
                ALTER TABLE job_applications 
                ADD COLUMN jsearch_salary_response TEXT
            """))
            print("  ✓ Added jsearch_salary_response column")
        else:
            print("  - jsearch_salary_response already exists")
        
        print("✅ Migration complete!")


if __name__ == "__main__":
    asyncio.run(migrate())
