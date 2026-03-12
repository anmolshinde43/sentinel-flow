import sqlite3
from datetime import datetime, timedelta
import smtplib # For actual email sending
from email.message import EmailMessage

DB_NAME = 'evaluations.db'

# 1. The Notification Function
def send_notification(assessor_email, employee_name, task_name, due_date):
    """
    Sends an urgent reminder to the assessor.
    In a real demo, we print to console. For a real email, we use SMTP.
    """
    subject = f"URGENT: Evaluation Due for {employee_name}"
    body = f"""
    Hello,
    
    This is an automated reminder from the Sentinel-Flow Platform.
    The following evaluation is due in 48 hours:
    
    - Employee: {employee_name}
    - Task: {task_name}
    - Due Date: {due_date}
    
    Please click the link below to access the assessment form:
    http://sentinel-flow.industrial/assess/{employee_name.replace(' ', '_')}
    
    Governance Protocol: Failure to complete this may delay contract confirmation.
    """

    # --- MOCK OUTPUT (For your Examiners to see) ---
    print("\n" + "="*50)
    print(f"📧 OUTGOING EMAIL TO: {assessor_email}")
    print(f"SUBJECT: {subject}")
    print(f"CONTENT: {body.strip()}")
    print("="*50)

    # --- REAL SMTP LOGIC (Commented out so it doesn't crash without credentials) ---
    """
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "alerts@sentinel-flow.com"
    msg['To'] = assessor_email
    
    # Example for Gmail (requires App Password)
    # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    #     smtp.login('YOUR_EMAIL', 'YOUR_PASSWORD')
    #     smtp.send_message(msg)
    """

# 2. The Logic: Checking for tasks due in exactly 48 hours
def check_upcoming_notifications():
    print(f"\n[SYSTEM] Scanning for tasks due in 48 hours...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Calculate the "Warning Date" (Today + 2 days)
    warning_date = (datetime.now() + timedelta(days=2)).date().isoformat()
    
    # Query: Join Evaluation Tasks with Employee names
    # For demo purposes, we'll assume a dummy email for the assessor
    cursor.execute('''
        SELECT e.name, t.task_name, t.due_date, t.assigned_to 
        FROM evaluation_tasks t
        JOIN employees e ON t.employee_id = e.id
        WHERE t.due_date = ? AND t.status = 'Pending'
    ''', (warning_date,))
    
    upcoming_tasks = cursor.fetchall()
    
    if upcoming_tasks:
        for emp_name, task_name, due_date, assigned_role in upcoming_tasks:
            # Map roles to dummy emails
            assessor_email = f"{assigned_role.lower().replace(' ', '.')}@company.com"
            send_notification(assessor_email, emp_name, task_name, due_date)
    else:
        print(f"No tasks found for due date: {warning_date}")
        
    conn.close()

# --- RUNNING THE TEST ---
if __name__ == "__main__":
    # Note: This assumes you ran the Task 2 code already to create 'evaluations.db'
    # If not, let's inject one "Alex P." case for the demo:
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create a test case for Alex P. due in exactly 2 days
    two_days_out = (datetime.now() + timedelta(days=2)).date().isoformat()
    cursor.execute("INSERT INTO employees (name, role, start_date) VALUES ('Alex P.', 'Factory Intern', '2026-03-01')")
    emp_id = cursor.lastrowid
    cursor.execute("INSERT INTO evaluation_tasks (employee_id, task_name, due_date, assigned_to) VALUES (?, ?, ?, ?)",
                   (emp_id, '30-Day Safety Check', two_days_out, 'Safety Officer'))
    conn.commit()
    conn.close()

    # Trigger the check
    check_upcoming_notifications()
