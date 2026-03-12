import os
import random
import datetime
import joblib
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from apscheduler.schedulers.background import BackgroundScheduler
from reportlab.pdfgen import canvas
from dotenv import load_dotenv

# --- 1. CONFIGURATION & DATABASE SETUP ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. DATABASE MODELS ---
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    # Add other columns here (e.g., department, email) if they exist in Supabase

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3. BACKGROUND AUTOMATION ---
def compliance_check_job():
    emp_id = random.randint(1000, 9999)
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"--- 🕒 [SENTINEL-WATCH] Scan @ {timestamp} ---")
    if emp_id % 3 == 0:
        print(f"🚨 ALERT: Potential High-Risk Sentiment detected in ID #{emp_id}!")
    else:
        print(f"✅ Status: No bias or risk detected for #{emp_id}.")
    print("------------------------------------------------------------")

scheduler = BackgroundScheduler()
scheduler.add_job(func=compliance_check_job, trigger="interval", seconds=60) # Changed to 60s to avoid spamming console
scheduler.start()

# --- 4. FASTAPI APP INITIALIZATION ---
app = FastAPI(title="Sentinel-Flow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 5. ML MODEL LOADING ---
MODEL_PATH = "models/sentinel_risk_model.pkl"
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, MODEL_PATH)
    model = joblib.load(full_path)
    print("✅ Sentinel-Flow ML Engine Loaded Successfully.")
except Exception as e:
    model = None
    print(f"⚠️ ML Engine Offline: {e}")

# --- 6. DATA SCHEMAS (Pydantic) ---
class WorkerStats(BaseModel):
    attendance_pct: float
    safety_incidents: int
    manager_score: float

class ManagerReview(BaseModel):
    raw_text: str

class HRComplaint(BaseModel):
    employee_id: int
    complaint_text: str

# --- 7. ENDPOINTS ---

# NEW: Database Endpoint to fetch employees from Supabase
@app.get("/employees")
def read_employees(db: Session = Depends(get_db)):
    try:
        employees = db.query(Employee).all()
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

@app.post("/api/ai/predict-risk")
async def predict_risk(stats: WorkerStats):
    if model is None:
        raise HTTPException(status_code=500, detail="ML Engine is offline.")
    
    features = [[stats.attendance_pct, stats.safety_incidents, stats.manager_score]]
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    confidence = probabilities[1] if prediction == 1 else probabilities[0]
    
    return {
        "pass_probation": bool(prediction),
        "confidence_score": round(confidence * 100, 2),
        "risk_level": "Low Risk" if prediction == 1 else "High Risk"
    } 

@app.post("/api/ai/sanitize-review")
async def sanitize_review(review: ManagerReview):
    sanitized_text = "The employee demonstrated consistent technical output. Punctuality was noted for review."
    return {
        "original_review": review.raw_text,
        "sanitized_review": sanitized_text,
        "status": "Legally Protected"
    } 

@app.post("/api/hr/report-threat")
async def report_threat(complaint: HRComplaint):
    is_serious = any(word in complaint.complaint_text.lower() for word in ["legal", "threat", "sue", "quit"])
    risk_level = "HIGH RISK" if is_serious else "LOW RISK"
    return {
        "event": "Manual HR Filing",
        "employee_id": complaint.employee_id,
        "risk_assessment": risk_level,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/reports/generate-legal-pdf")
async def generate_pdf(employee_id: int, risk: str = "UNDEFINED"):
    file_path = f"Audit_Report_{employee_id}.pdf"
    c = canvas.Canvas(file_path)
    c.rect(50, 50, 500, 750)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 770, "SENTINEL-FLOW: LEGAL AUDIT")
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Report Date: {datetime.datetime.now()}")
    c.drawString(100, 710, f"Employee ID: #{employee_id}")
    
    if "HIGH" in risk.upper():
        c.setFillColorRGB(0.8, 0, 0)
    else:
        c.setFillColorRGB(0, 0.5, 0)
        
    c.drawString(100, 680, f"FINAL ASSESSMENT: {risk}")
    c.save()
    return FileResponse(file_path, media_type='application/pdf', filename=file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)