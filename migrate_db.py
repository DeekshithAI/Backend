"""
Database migration script to add new columns to existing tables
Run this to update your existing database with new columns
"""

from sqlalchemy import text
from db.database import engine

def run_migration():
    """Add new columns to existing tables"""
    
    migrations = [
        # Farmer table - add created_at
        """
        ALTER TABLE farmers 
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """,
        
        # Survey table - add topview_image_path, extra_data, created_at
        """
        ALTER TABLE surveys 
        ADD COLUMN IF NOT EXISTS topview_image_path VARCHAR;
        """,
        """
        ALTER TABLE surveys 
        ADD COLUMN IF NOT EXISTS extra_data JSON DEFAULT '{}';
        """,
        """
        ALTER TABLE surveys 
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """,
        
        # Tree table - add extra_data, created_at (cx and cy should already exist)
        """
        ALTER TABLE trees 
        ADD COLUMN IF NOT EXISTS extra_data JSON DEFAULT '{}';
        """,
        """
        ALTER TABLE trees 
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """,
        
        # TreePart table - add status, extra, timestamp (if they don't exist)
        """
        ALTER TABLE tree_parts 
        ADD COLUMN IF NOT EXISTS status VARCHAR;
        """,
        """
        ALTER TABLE tree_parts 
        ADD COLUMN IF NOT EXISTS extra JSON DEFAULT '{}';
        """,
        """
        ALTER TABLE tree_parts 
        ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """,
    ]
    
    print("[*] Running database migration...")
    print("=" * 60)
    
    with engine.connect() as conn:
        for i, migration in enumerate(migrations, 1):
            try:
                conn.execute(text(migration))
                conn.commit()
                # Extract table name from migration
                table = migration.split("ALTER TABLE")[1].split()[0].strip()
                column = migration.split("ADD COLUMN IF NOT EXISTS")[1].split()[0].strip()
                print("[OK] {}. Added {} to {}".format(i, column, table))
            except Exception as e:
                print("[!!] {}. Migration failed (might already exist): {}".format(i, e))
    
    print("=" * 60)
    print("[OK] Migration completed!")
    print("\nYou can now restart your server and test the API endpoints.")

if __name__ == "__main__":
    run_migration()
