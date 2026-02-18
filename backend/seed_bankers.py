"""
Seed Bankers Script
====================
Creates 3 test banker accounts in MySQL.
Run:  python -m backend.seed_bankers
"""

from backend.database import SessionLocal, engine, Base
from backend.models import Banker
from backend.auth_service import hash_password

# Ensure tables exist
Base.metadata.create_all(bind=engine)

TEST_BANKERS = [
    {
        "banker_name": "Raj Kumar",
        "email": "raj.kumar@bank.com",
        "phone": "+91-98765-43210",
        "branch_code": "NYC-001",
        "password": "password123",
    },
    {
        "banker_name": "Priya Singh",
        "email": "priya.singh@bank.com",
        "phone": "+91-98765-43211",
        "branch_code": "NYC-002",
        "password": "password123",
    },
    {
        "banker_name": "Amit Patel",
        "email": "amit.patel@bank.com",
        "phone": "+91-98765-43212",
        "branch_code": "LAX-001",
        "password": "password123",
    },
]


def seed():
    db = SessionLocal()
    try:
        for data in TEST_BANKERS:
            existing = db.query(Banker).filter(Banker.email == data["email"]).first()
            if existing:
                print(f"⏭  Banker already exists: {data['email']}")
                continue
            banker = Banker(
                banker_name=data["banker_name"],
                email=data["email"],
                phone=data["phone"],
                branch_code=data["branch_code"],
                password_hash=hash_password(data["password"]),
            )
            db.add(banker)
            db.commit()
            print(f"✅ Created banker: {data['banker_name']} ({data['email']})")
        print("\n🎉 Seeding complete!")
        print("Login credentials:")
        for data in TEST_BANKERS:
            print(f"  Email: {data['email']}  |  Password: {data['password']}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
