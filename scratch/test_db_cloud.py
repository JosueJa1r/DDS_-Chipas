import os
import mysql.connector

def test_connection():
    env_vars = {}
    
    # 1. Parse .env manually to test
    if os.path.exists(".env"):
        print("Reading .env file...")
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("=", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip()
                    env_vars[key] = val
                    # Also set it in os.environ for testing
                    os.environ[key] = val
                    
        print(f"Variables parsed: {list(env_vars.keys())}")
    else:
        print("Error: .env file not found!")
        return

    # 2. Get connection parameters
    host = env_vars.get("host", "localhost")
    user = env_vars.get("user", "root")
    password = env_vars.get("password")
    database = env_vars.get("database", "bd_agricultura_chiapas")
    port = env_vars.get("port", "3306")

    print(f"\nAttempting connection to cloud MySQL:")
    print(f"  Host: {host}")
    print(f"  User: {user}")
    print(f"  Database: {database}")
    print(f"  Port: {port}")
    
    try:
        conexion = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            connect_timeout=10 # 10 seconds timeout
        )
        if conexion.is_connected():
            print("\nSUCCESS: Connected to cloud MySQL database successfully!")
            cursor = conexion.cursor()
            cursor.execute("SELECT VERSION()")
            db_version = cursor.fetchone()
            print(f"Database Server Version: {db_version[0]}")
            
            # Check tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"Tables in cloud database ({len(tables)}):")
            for t in tables[:5]:
                print(f"  - {t[0]}")
                
            cursor.close()
            conexion.close()
        else:
            print("\nFAILED: Connection call returned but was not connected.")
    except Exception as e:
        print(f"\nFAILED: Could not connect to cloud database.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    test_connection()
