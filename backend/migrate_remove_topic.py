"""
Database migration script to remove the 'topic' column from the stories table.
Run this script to clean up the database after removing topic from the schema.
"""

import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "stories.db")

def migrate_database():
    """Remove the topic column from the stories table."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Starting database migration...")
        
        # Check if topic column exists
        cursor.execute("PRAGMA table_info(stories)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'topic' not in column_names:
            print("Topic column does not exist. Migration not needed.")
            return
        
        print("Topic column found. Creating new table without topic column...")
        
        # Create new table without topic column
        cursor.execute("""
            CREATE TABLE stories_new (
                id INTEGER PRIMARY KEY,
                title VARCHAR,
                person VARCHAR,
                emotion VARCHAR,
                notes TEXT,
                generated_speech TEXT,
                album_json TEXT,
                used_in_presentation BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # Copy data from old table to new table (excluding topic)
        cursor.execute("""
            INSERT INTO stories_new 
            (id, title, person, emotion, notes, generated_speech, album_json, 
             used_in_presentation, created_at, updated_at)
            SELECT id, title, person, emotion, notes, generated_speech, album_json,
                   used_in_presentation, created_at, updated_at
            FROM stories
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE stories")
        
        # Rename new table to original name
        cursor.execute("ALTER TABLE stories_new RENAME TO stories")
        
        # Commit changes
        conn.commit()
        
        print("Migration completed successfully!")
        print("Topic column has been removed from the stories table.")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
