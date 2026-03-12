import sqlite3
import json
from datetime import datetime, timedelta

DB_NAME = 'evaluations.db'

# 1. Setup the Databases
def setup_orchestrator_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table for Employees
    cursor.execute('DROP TABLE IF EXISTS employees')
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            start_date TEXT
        )
    ''')
    
    # Table for the generated Evaluation Tasks
    cursor.execute('DROP TABLE IF EXISTS evaluation_tasks')
    cursor.execute('''
        CREATE TABLE evaluation_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            task_name TEXT,
            due_date TEXT,
            assigned_to TEXT,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

# 2. The JSON Template Logic (The "Recipe")
# In a real app, this would be a .json file or a separate DB table
ROLE_TEMPLATES = {
    "Software Intern": [
        {"milestone": "Initial Code Review", "offset_days": 15, "assignee": "Senior Dev"},
        {"milestone": "Mid-Probation Tech Assessment", "offset_days": 45, "assignee": "CTO"},
        {"milestone": "Final Project Demo", "offset_days": 85, "assignee": "HR Head"}
    ],
    "Factory Intern": [
        {"milestone": "Safety Drill Compliance", "offset_days": 7, "assignee": "Safety Officer"},
        {"milestone": "Machine Operation Test", "offset_days": 30, "assignee": "Floor Manager"},
        {"milestone": "Final Safety Certification", "offset_days": 90, "assignee": "Site Head"}
    ]
}

# 3. The Orchestrator Function
def add_employee_and_generate_workflow(name, role, start_date_str):
    print(f"\n[SYSTEM] Adding new {role}: {name}...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Insert employee
    cursor.execute('INSERT INTO employees (name, role, start_date) VALUES (?, ?, ?)', 
                   (name, role, start_date_str))
    emp_id = cursor.lastrowid
    
    # Parse the start date
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    # Fetch the specific template for the role
    template = ROLE_TEMPLATES.get(role)
    
    if template:
        print(f"[ORCHESTRATOR] Template found. Generating {len(template)} milestones...")
        for step in template:
            # Logic: Calculate Due Date = Start Date + Offset
            due_date = (start_date + timedelta(days=step['offset_days'])).date().isoformat()
            
            # Insert into evaluation_tasks
            cursor.execute('''
                INSERT INTO evaluation_tasks (employee_id, task_name, due_date, assigned_to)
                VALUES (?, ?, ?, ?)
            ''', (emp_id, step['milestone'], due_date, step['assignee']))
            
            print(f" -> Scheduled: '{step['milestone']}' for {due_date} (Assigned to: {step['assignee']})")
        
        conn.commit()
    else:
        print(f"[ERROR] No template found for role: {role}")
    
    conn.close()

# --- RUNNING THE TEST ---
if __name__ == "__main__":
    setup_orchestrator_db()
    
    # Example 1: Software Intern starting March 1st
    add_employee_and_generate_workflow("Meeth", "Software Intern", "2026-03-01")
    
    # Example 2: Factory Intern starting March 1st
    add_employee_and_generate_workflow("John Doe", "Factory Intern", "2026-03-01")
