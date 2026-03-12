import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Employee, Base  # Imports your model from main.py
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed():
    db = SessionLocal()
    # Check if we already have employees
    if db.query(Employee).count() == 0:
        print("🌱 Seeding database with test employees...")
        test_data = [
            Employee(name="Sarah Chen", email="sarah.c@company.com", role="Software Engineer", salary=95000),
            Employee(name="Marcus Wright", email="m.wright@company.com", role="Safety Officer", salary=72000),
            Employee(name="Elena Rodriguez", email="elena.r@company.com", role="Project Manager", salary=88000),
        ]
        db.add_all(test_data)
        db.commit()
        print("✅ Success! 3 employees added.")
    else:
        print("ℹ️ Database already has data. Skipping seed.")
    db.close()

if __name__ == "__main__":
    seed()