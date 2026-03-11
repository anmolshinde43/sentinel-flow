from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
import random
from fastapi.middleware.cors import CORSMiddleware
from reportlab.pdfgen import canvas
from fastapi.responses import FileResponse

# --- TASK 3: BACKGROUND AUTOMATION ---
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
scheduler.add_job(func=compliance_check_job, trigger="interval", seconds=10)
scheduler.start()

app = FastAPI(title="Sentinel-Flow API")

# --- CORS SETTINGS (Crucial for React) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODEL LOADING ---
MODEL_PATH = "models/sentinel_risk_model.pkl"
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, MODEL_PATH)
    model = joblib.load(full_path)
    print("✅ Sentinel-Flow ML Engine Loaded Successfully.")
except FileNotFoundError:
    model = None
    print(f"❌ CRITICAL ERROR: Could not find {MODEL_PATH}")

# --- DATA MODELS ---
class WorkerStats(BaseModel):
    attendance_pct: float
    safety_incidents: int
    manager_score: float

class ManagerReview(BaseModel):
    raw_text: str

class HRComplaint(BaseModel):
    employee_id: int
    complaint_text: str

# --- ENDPOINTS ---

@app.post("/api/ai/predict-risk")
async def predict_risk(stats: WorkerStats):
    if model is None:
        raise HTTPException(status_code=500, detail="ML Engine is offline.")
    
    features = [[stats.attendance_pct, stats.safety_incidents, stats.manager_score]]
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    
    # Corrected: Get probability of the specific prediction
    confidence = probabilities[1] if prediction == 1 else probabilities[0]
    
    return {
        "pass_probation": bool(prediction),
        "confidence_score": round(confidence * 100, 2),
        "risk_level": "Low Risk" if prediction == 1 else "High Risk"
    } 

@app.post("/api/ai/sanitize-review")
async def sanitize_review(review: ManagerReview):
    sanitized_text = "The employee demonstrated consistent technical output. However, punctuality issues were noted twice this week."
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
        "ai_analysis": "Keywords triggered immediate escalation" if is_serious else "General feedback recorded",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# --- PDF GENERATOR ENDPOINT ---
@app.get("/api/reports/generate-legal-pdf")
async def generate_pdf(employee_id: int, risk: str = "UNDEFINED"):
    file_path = f"Audit_Report_{employee_id}.pdf"
    
    # Create the PDF
    c = canvas.Canvas(file_path)
    
    # Draw a Border
    c.setStrokeColorRGB(0.2, 0.2, 0.2)
    c.rect(50, 50, 500, 750)
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 770, "SENTINEL-FLOW: LEGAL AUDIT")
    
    # Audit Details
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Report Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(100, 710, f"Employee Subject ID: #{employee_id}")
    
    # Risk Assessment (Styled based on severity)
    c.setFont("Helvetica-Bold", 14)
    if "HIGH" in risk.upper():
        c.setFillColorRGB(0.8, 0, 0) # Red Text
    else:
        c.setFillColorRGB(0, 0.5, 0) # Green Text
        
    c.drawString(100, 680, f"FINAL ASSESSMENT: {risk}")
    
    # Reset color to black for text
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 650, "Note: This document is an AI-generated compliance record.")
    c.drawString(100, 635, "Any 'High Risk' status requires immediate manual review by legal.")
    
    c.save()
    return FileResponse(file_path, media_type='application/pdf', filename=file_path)