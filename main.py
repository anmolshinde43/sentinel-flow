import os
import random
import datetime
import joblib
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# --- 1. DATABASE SETUP ---
load_dotenv()
# Ensure your .env has DATABASE_URL="postgresql+psycopg2://..."
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. DATABASE MODELS ---
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    role = Column(String)
    salary = Column(Float, default=0.0)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3. DATA SCHEMAS (Pydantic) ---
class EmployeeCreate(BaseModel):
    name: str
    role: str
    email: str
    salary: float

# --- 4. APP INITIALIZATION ---
app = FastAPI(title="Sentinel Flow Backend")

# ENABLE CORS - Essential for your frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 5. DASHBOARD ENDPOINTS ---

@app.get("/api/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Returns counts for the dashboard top cards."""
    try:
        active_count = db.query(Employee).count()
        # We'll keep pending reviews as a mock number or count specific logic
        return {
            "active_employees": active_count,
            "pending_reviews": 4 
        }
    except Exception as e:
        return {"error": str(e), "active_employees": 0, "pending_reviews": 0}

@app.get("/api/milestones")
def get_milestones(db: Session = Depends(get_db)):
    """Returns the most recent 3-5 employees for the 'Recent Audit' table."""
    try:
        employees = db.query(Employee).order_by(Employee.id.desc()).limit(5).all()
        
        milestones = []
        for emp in employees:
            milestones.append({
                "name": emp.name,
                "milestone": f"{emp.role} Audit",
                "status": "Done" if (emp.salary or 0) > 0 else "In Progress"
            })
        return milestones
    except Exception as e:
        return []

# --- 6. CRUD ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "Sentinel Flow Backend is active"}

@app.get("/employees")
def get_all_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@app.post("/employees")
def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    new_employee = Employee(
        name=emp.name,
        email=emp.email,
        role=emp.role,
        salary=emp.salary
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@app.get("/employees/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

# --- 7. RUN SERVER ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)