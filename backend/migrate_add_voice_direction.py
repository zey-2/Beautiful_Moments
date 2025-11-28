import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SQLALCHEMY_DATABASE_URL

def migrate():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE stories ADD COLUMN generated_voice_direction TEXT"))
            print("Successfully added generated_voice_direction column to stories table")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("Column generated_voice_direction already exists")
            else:
                print(f"Error adding column: {e}")

if __name__ == "__main__":
    migrate()
