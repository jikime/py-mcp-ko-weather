import sqlite3
from pathlib import Path

def get_grid_location(city, gu, dong):
    """
    Get grid location (nx, ny) for Korea Weather
    
    Args:
        city: City Name (e.g. 서울특별시)
        gu: Gu Name (e.g. 서초구)
        dong: Dong Name (e.g. 양재1동)
        
    Returns:
        tuple: (nx, ny) grid coordinates or None if not found
    """
    db_path = Path(__file__).parent / "data" / "weather_grid.db"
    
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            SELECT grid_x, grid_y 
            FROM weather_grid 
            WHERE level1 = ? AND level2 = ? AND level3 = ?
            """, 
            (city, gu, dong)
        )
        result = cursor.fetchone()
        
        if result:
            return result
        else:
            return None
    finally:
        conn.close()

def main():
    print("Hello from py-mcp-ko-weather!")
    
    # Example usage
    try:
        grid = get_grid_location("서울특별시", "서초구", "양재1동")
        if grid:
            nx, ny = grid
            print(f"Grid coordinates for 서울특별시 서초구 양재1동: X={nx}, Y={ny}")
        else:
            print("Location not found in database")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
