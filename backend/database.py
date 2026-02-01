import sqlite3
import json
import os

DB_PATH = "civic_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS authority_cache (
            key TEXT PRIMARY KEY,
            category TEXT,
            location TEXT,
            data TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_db_key(category, location):
    return f"{category.lower()}_{location.lower()}"

def save_authority(category, location, data):
    key = get_db_key(category, location)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Serialize dict to json string
    data_json = json.dumps(data)
    c.execute('''
        INSERT OR REPLACE INTO authority_cache (key, category, location, data, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (key, category, location, data_json))
    conn.commit()
    conn.close()
    print(f"DB: Saved authority data for {key}")

def get_cached_authority(category, location):
    key = get_db_key(category, location)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT data FROM authority_cache WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    if row:
        print(f"DB: Retrieved authority data for {key}")
        return json.loads(row[0])
    return None
