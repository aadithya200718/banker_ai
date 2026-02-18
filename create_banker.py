
from backend.database import SessionLocal, engine, Base
from backend.models import Banker
from backend.auth_service import hash_password

def create_test_banker():
    db = SessionLocal()
    try:
        # Check if banker exists
        email = "banker@hdfc.com"
        existing = db.query(Banker).filter(Banker.email == email).first()
        
        if existing:
            print(f"Banker {email} already exists.")
            return

        # Create new banker
        new_banker = Banker(
            banker_name="Adithya (Test)",
            email=email,
            password_hash=hash_password("password123"), # Default password
            branch_code="HDFC001",
            is_active=True
        )
        db.add(new_banker)
        db.commit()
        print(f"Successfully created banker: {email} / password123")
        
    except Exception as e:
        print(f"Error creating banker: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating test banker...")
    create_test_banker()
