
import pymysql
import sys
import os

def update_env(host, port, user, password, db_name):
    env_path = ".env"
    try:
        with open(env_path, "r") as f:
            lines = f.readlines()
            
        new_lines = []
        for line in lines:
            if line.startswith("DATABASE_HOST="):
                new_lines.append(f"DATABASE_HOST={host}\n")
            elif line.startswith("DATABASE_PORT="):
                new_lines.append(f"DATABASE_PORT={port}\n")
            elif line.startswith("DATABASE_USER="):
                new_lines.append(f"DATABASE_USER={user}\n")
            elif line.startswith("DATABASE_PASSWORD="):
                new_lines.append(f"DATABASE_PASSWORD={password}\n")
            elif line.startswith("DATABASE_NAME="):
                new_lines.append(f"DATABASE_NAME={db_name}\n")
            elif line.startswith("DATABASE_URL="):
                 # URL encode password for special chars if needed, simplified here
                encoded_pwd = password.replace("@", "%40").replace(":", "%3A").replace("/", "%2F")
                new_lines.append(f"DATABASE_URL=mysql+pymysql://{user}:{encoded_pwd}@{host}:{port}/{db_name}\n")
            else:
                new_lines.append(line)
        
        with open(env_path, "w") as f:
            f.writelines(new_lines)
        print("✅ .env file updated successfully!")
    except Exception as e:
        print(f"❌ Failed to update .env: {e}")

def main():
    print("\n=== MySQL Database Setup Wizard ===")
    print("This script will help you connect to your local MySQL server.")
    
    host = input("Enter MySQL Host [localhost]: ").strip() or "localhost"
    port_str = input("Enter MySQL Port [3306]: ").strip() or "3306"
    user = input("Enter MySQL User [root]: ").strip() or "root"
    password = input("Enter MySQL Password: ").strip()
    
    try:
        port = int(port_str)
        print(f"\nConnecting to {user}@{host}:{port}...")
        
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ Connection successful!")
        
        db_name = "banker_verification"
        with connection.cursor() as cursor:
            print(f"Checking for database '{db_name}'...")
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
            if cursor.fetchone():
                print(f"✅ Database '{db_name}' already exists.")
            else:
                print(f"Creating database '{db_name}'...")
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"✅ Database '{db_name}' created!")

        connection.close()
        
        print("\nUpdating configuration...")
        update_env(host, port, user, password, db_name)
        print("\nSetup Complete! You can now restart the backend server.")

    except pymysql.err.OperationalError as e:
        print(f"\n❌ Connection Failed: {e}")
        print("Please check your password and ensure MySQL is running.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
