"""
Migration script to add audio_file_path column to stories table.
Run this script to update the database schema.
"""
from sqlalchemy import create_engine, text

SQLALCHEMY_DATABASE_URL = "sqlite:///./stories.db"

def migrate():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Add the column using raw SQL
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE stories ADD COLUMN audio_file_path VARCHAR"))
            conn.commit()
            print("Successfully added audio_file_path column to stories table")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("Column audio_file_path already exists")
            else:
                print(f"Error during migration: {e}")
                raise

if __name__ == "__main__":
    migrate()
