from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, SessionLocal
from models import Employee
from schemas import EmployeeCreate

app = FastAPI()

# --- 1. ENABLE CORS ---
# This is required for your frontend (Live Server) to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. DASHBOARD ENDPOINTS ---

@app.get("/api/stats")
def get_dashboard_stats():
    db = SessionLocal()
    try:
        # Count real employees from your database
        active_count = db.query(Employee).count()
        # Mocking pending reviews for now, or you can count employees with specific status
        pending_count = 2 
        
        return {
            "active_employees": active_count,
            "pending_reviews": pending_count
        }
    finally:
        db.close()

@app.get("/api/milestones")
def get_milestones():
    db = SessionLocal()
    try:
        # Fetch the last 3 employees to show in the "Recent Audit" table
        employees = db.query(Employee).order_by(Employee.id.desc()).limit(3).all()
        
        milestones = []
        for emp in employees:
            milestones.append({
                "name": emp.name,
                "milestone": f"{emp.role} Onboarding",
                "status": "Done" if emp.salary > 0 else "In Progress" # Example logic
            })
        return milestones
    finally:
        db.close()

# --- 3. EXISTING CRUD ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "Sentinel Flow Backend is running"}

@app.post("/employees")
def create_employee(emp: EmployeeCreate):
    db = SessionLocal()
    try:
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
    finally:
        db.close()

@app.get("/employees/{employee_id}")
def get_employee(employee_id: int): # Changed to int to match standard DB IDs
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return {"message": "Employee not found"}
        return employee
    finally:
        db.close()

# ... (Keep your existing PUT and DELETE methods below) ...