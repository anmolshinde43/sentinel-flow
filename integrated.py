import sqlite3
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler

DB_NAME = 'sentinel_gateway.db'

# --- 1. THE SHARED DATABASE SETUP ---
def initialize_system():
    if os.path.exists(DB_NAME): os.remove(DB_NAME) # Fresh start for demo
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Unified Table: Employees (From Task 1 & 2)
    cursor.execute('''CREATE TABLE employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, role TEXT, status TEXT, 
        start_date TEXT, contract_end_date TEXT)''')
    
    # Unified Table: Evaluation Tasks (From Task 2 & 3)
    cursor.execute('''CREATE TABLE evaluation_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER, task_name TEXT, 
        due_date TEXT, assigned_to TEXT, status TEXT DEFAULT 'Pending',
        FOREIGN KEY(employee_id) REFERENCES employees(id))''')
    
    conn.commit()
    conn.close()
    print("🚀 System Initialized: Central Database Ready.")

# --- 2. INTEGRATED ORCHESTRATOR (Task 2) ---
ROLE_CONFIG = {
    "Software Intern": {"offset": 45, "task": "Code Review", "assignee": "Senior Dev"},
    "Factory Intern": {"offset": 30, "task": "Machine Safety Test", "assignee": "Floor Manager"}
}

def add_new_hire(name, role, start_date_str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Calculate Contract End (6 months later for this example)
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = (start_dt + timedelta(days=180)).date().isoformat()
    
    cursor.execute("INSERT INTO employees (name, role, status, start_date, contract_end_date) VALUES (?,?,?,?,?)",
                   (name, role, 'Active', start_date_str, end_date))
    emp_id = cursor.lastrowid
    
    # Generate Task based on Role Logic
    config = ROLE_CONFIG.get(role)
    if config:
        due_date = (start_dt + timedelta(days=config['offset'])).date().isoformat()
        cursor.execute("INSERT INTO evaluation_tasks (employee_id, task_name, due_date, assigned_to) VALUES (?,?,?,?)",
                       (emp_id, config['task'], due_date, config['assignee']))
    
    conn.commit()
    conn.close()
    print(f"👤 Added {name} | Contract Ends: {end_date} | Task set for: {due_date}")

# --- 3. THE DUAL-ACTION SCHEDULER (Task 1 & 3 Combined) ---
def run_system_check():
    print(f"\n--- 🔍 SYSTEM SCAN: {datetime.now().strftime('%Y-%m-%d %H:%M')} ---")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ACTION A: Check for Contract Expiry in 14 Days (Task 1)
    target_14 = (datetime.now() + timedelta(days=14)).date().isoformat()
    cursor.execute("SELECT id, name FROM employees WHERE contract_end_date = ? AND status = 'Active'", (target_14,))
    expiring = cursor.fetchall()
    for eid, name in expiring:
        cursor.execute("UPDATE employees SET status = 'Action Required' WHERE id = ?", (eid,))
        print(f"⚠️ ALERT: {name}'s contract expires in 14 days. Dashboard Updated.")

    # ACTION B: Check for Pending Tasks due in 48 Hours (Task 3)
    target_48h = (datetime.now() + timedelta(days=2)).date().isoformat()
    cursor.execute('''SELECT e.name, t.task_name, t.assigned_to FROM evaluation_tasks t 
                      JOIN employees e ON t.employee_id = e.id 
                      WHERE t.due_date = ? AND t.status = 'Pending' ''', (target_48h,))
    reminders = cursor.fetchall()
    for emp_name, task, boss in reminders:
        print(f"📧 NOTIFICATION SENT to {boss}: '{task}' for {emp_name} is due in 48h!")

    conn.commit()
    conn.close()

# --- 4. EXECUTION ---
if __name__ == "__main__":
    initialize_system()
    
    # Setup some test data (Some expiring, some with tasks due)
    # 1. Someone hired 166 days ago (Contract ends in 14 days)
    hired_long_ago = (datetime.now() - timedelta(days=166)).date().isoformat()
    add_new_hire("Alice Expiring", "Software Intern", hired_long_ago)
    
    # 2. Someone hired 28 days ago (Evaluation Task due in 2 days)
    hired_recently = (datetime.now() - timedelta(days=28)).date().isoformat()
    add_new_hire("Bob Newbie", "Factory Intern", hired_recently)

    # Start Scheduler
    scheduler = BlockingScheduler()
    # Demo Mode: Runs every 15 seconds
    scheduler.add_job(run_system_check, 'interval', seconds=15)
    
    print("\nIntegrated Engine Running. Checking DB every 15s...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
