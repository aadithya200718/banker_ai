import os
import sys
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_tidb_connection():
    print("----------------------------------------------------------------")
    print("Create Verification Script - TiDB Connection Check")
    print("----------------------------------------------------------------")

    host = os.getenv("DATABASE_HOST")
    port = int(os.getenv("DATABASE_PORT", 4000))
    user = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PASSWORD")
    database = os.getenv("DATABASE_NAME", "banker_verification")
    ssl_ca = os.getenv("DATABASE_SSL_CA")

    print(f"Target: {host}:{port}")
    print(f"User:   {user}")
    print(f"DB:     {database}")
    print(f"SSL:    {ssl_ca if ssl_ca else 'Disabled'}")
    
    if not host or not user or not password:
        print("\n❌ Error: Missing required environment variables.")
        print("Please check your .env file and ensure DATABASE_HOST, DATABASE_USER, and DATABASE_PASSWORD are set.")
        return False

    ssl_config = None
    if ssl_ca:
        if os.path.exists(ssl_ca):
            ssl_config = {"ca": ssl_ca}
            print("✅ SSL CA file found.")
        else:
            print(f"⚠️ Warning: SSL CA file not found at {ssl_ca}. Connection might fail if SSL is required.")

    print("\nAttempting to connect...")
    
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            ssl=ssl_config,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10
        )
        
        print("✅ Connection Successful!")
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"Server Version: {version}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"Tables found: {len(tables)}")
            for table in tables:
                print(f" - {list(table.values())[0]}")
                
        conn.close()
        return True

    except pymysql.MySQLError as e:
        print(f"\n❌ Connection Failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    if verify_tidb_connection():
        print("\n✅ TiDB verification PASSED.")
        sys.exit(0)
    else:
        print("\n❌ TiDB verification FAILED.")
        sys.exit(1)
