from fastapi import FastAPI
from database import engine, SessionLocal
from models import Employee
from schemas import EmployeeCreate

app = FastAPI()

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
def get_employee(employee_id: str):
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()

        if not employee:
            return {"message": "Employee not found"}

        return employee
    finally:
        db.close()

@app.put("/employees/{employee_id}")
def update_employee(employee_id: str, emp: EmployeeCreate):
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()

        if not employee:
            return {"message": "Employee not found"}

        employee.name = emp.name
        employee.email = emp.email
        employee.role = emp.role
        employee.salary = emp.salary

        db.commit()
        db.refresh(employee)

        return employee
    finally:
        db.close()

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: str):
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()

        if not employee:
            return {"message": "Employee not found"}

        db.delete(employee)
        db.commit()

        return {"message": "Employee deleted"}
    finally:
        db.close()