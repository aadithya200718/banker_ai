
import pymysql
import sys

def try_connect(password):
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.err.OperationalError as e:
        return None

def setup():
    print("Attempting to connect to MySQL...")
    
    # Try 1: Password from .env
    password_attempt = "manaadithya@123"
    conn = try_connect(password_attempt)
    success_password = None

    if conn:
        print(f"✅ Connected with password: '{password_attempt}'")
        success_password = password_attempt
    else:
        print(f"❌ Failed with password: '{password_attempt}'")
        # Try 2: No password
        print("Attempting to connect with NO password...")
        conn = try_connect("")
        if conn:
            print("✅ Connected with EMPTY password")
            success_password = ""
        else:
            print("❌ Failed with EMPTY password")
    
    if conn is None:
        print("\n❌ Could not connect to MySQL.")
        print("Please check if:")
        print("1. MySQL Server is running (XAMPP/WAMP/MySQL Workbench)")
        print("2. The username is 'root'")
        print("3. You know the root password")
        sys.exit(1)

    try:
        with conn.cursor() as cursor:
            print("\nCheck database 'banker_verification'...")
            cursor.execute("SHOW DATABASES LIKE 'banker_verification'")
            result = cursor.fetchone()
            if result:
                print("✅ Database 'banker_verification' already exists.")
            else:
                print("⚠️ Database 'banker_verification' not found. Creating...")
                cursor.execute("CREATE DATABASE banker_verification")
                print("✅ Database 'banker_verification' created successfully!")
                
        print("\n--- ACTION REQUIRED ---")
        if success_password != "manaadithya@123":
            print(f"UPDATE your .env file!")
            print(f"Current: DATABASE_PASSWORD=manaadithya@123")
            print(f"Change to: DATABASE_PASSWORD={success_password}")
            
    finally:
        conn.close()

if __name__ == "__main__":
    setup()
