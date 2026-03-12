import requests
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler

API_URL = "http://127.0.0.1:8000/employees"


ROLE_CONFIG = {
    "Software Intern": {
        "offset": 45,
        "task": "Code Review",
        "assignee": "Senior Dev"
    },
    "Factory Intern": {
        "offset": 30,
        "task": "Machine Safety Test",
        "assignee": "Floor Manager"
    }
}


def add_new_hire(name, role, start_date):

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")

    contract_end = (start_dt + timedelta(days=180)).date().isoformat()

    data = {
        "name": name,
        "email": f"{name.lower().replace(' ', '.')}@company.com",
        "role": role,
        "salary": 20000,
        "manager_id": None,
        "contract_start": start_date,
        "contract_end": contract_end
    }

    response = requests.post(API_URL, json=data)

    employee = response.json()

    config = ROLE_CONFIG.get(role)

    if config:

        due_date = (start_dt + timedelta(days=config["offset"])).date()

        print(
            f"👤 {name} added | Task: {config['task']} "
            f"Due: {due_date}"
        )


def run_system_check():

    print("\n--- SYSTEM SCAN ---")

    response = requests.get(API_URL)

    employees = response.json()

    today = datetime.now().date()

    for emp in employees:

        contract_end = datetime.fromisoformat(emp["contract_end"]).date()

        if contract_end - today == timedelta(days=14):

            print(
                f"⚠️ ALERT: {emp['name']} contract expires in 14 days"
            )


if __name__ == "__main__":

    # demo employees
    add_new_hire("Alice Expiring", "Software Intern", "2025-09-01")

    add_new_hire("Bob Newbie", "Factory Intern", "2026-02-01")

    scheduler = BlockingScheduler()

    scheduler.add_job(run_system_check, "interval", seconds=15)

    print("Automation engine running...")

    scheduler.start()
