#!/usr/bin/env python3
import os
import pandas as pd
import sqlite3
from pathlib import Path

def migrate_excel_to_sqlite():
    """
    Migrate data from nxy.xlsx Excel file to SQLite database.
    Reads the fields: "1단계", "2단계", "3단계", "격자 X", "격자 Y"
    """
    # Define paths
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    excel_file = data_dir / "nxy.xlsx"
    db_file = data_dir / "weather_grid.db"
    
    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Check if Excel file exists
    if not excel_file.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_file}")
    
    # Read Excel file
    print(f"Reading Excel file: {excel_file}")
    df = pd.read_excel(excel_file)
    
    # Check if required columns exist
    required_columns = ["1단계", "2단계", "3단계", "격자 X", "격자 Y"]
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Required column '{column}' not found in Excel file")
    
    # Create SQLite database
    print(f"Creating SQLite database: {db_file}")
    conn = sqlite3.connect(db_file)
    
    # Create table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS weather_grid (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level1 TEXT,
        level2 TEXT,
        level3 TEXT,
        grid_x INTEGER,
        grid_y INTEGER,
        UNIQUE(level1, level2, level3)
    )
    ''')
    
    # Insert data
    print("Inserting data into database...")
    for _, row in df.iterrows():
        conn.execute(
            '''
            INSERT OR REPLACE INTO weather_grid 
            (level1, level2, level3, grid_x, grid_y) 
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                row["1단계"],
                row["2단계"],
                row["3단계"],
                row["격자 X"],
                row["격자 Y"]
            )
        )
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Migration completed successfully")
    
    # Print summary
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM weather_grid")
    count = cursor.fetchone()[0]
    print(f"Total records in database: {count}")
    conn.close()

if __name__ == "__main__":
    migrate_excel_to_sqlite()
