import mysql.connector

def check():
    try:
        conexion = mysql.connector.connect(
            host="localhost", 
            user="root",
            password="Pentathlon1938",
            database="bd_agricultura_chiapas", 
            port="3306"
        )
        cursor = conexion.cursor()
        
        # List tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tables in database:")
        for t in tables:
            print(t[0])
            
        for t in tables:
            table_name = t[0]
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            print(f"\nStructure of {table_name}:")
            for col in columns:
                print(f"  {col[0]} ({col[1]})")
                
            # Sample data
            cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 3")
            rows = cursor.fetchall()
            print(f"  Sample data ({len(rows)} rows):")
            for r in rows:
                print("   ", r)
        
        cursor.close()
        conexion.close()
    except Exception as e:
        print("Error connecting to DB:", e)

if __name__ == "__main__":
    check()
