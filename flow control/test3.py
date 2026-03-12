import requests
from datetime import datetime, timedelta


API_URL = "http://127.0.0.1:8000/employees"


def send_notification(email, employee_name, task_name, due_date):

    subject = f"URGENT: Evaluation Due for {employee_name}"

    body = f"""
Hello,

Automated reminder from Sentinel-Flow.

Employee: {employee_name}
Task: {task_name}
Due Date: {due_date}

Please complete the evaluation.
"""

    print("\n" + "=" * 50)
    print(f"📧 EMAIL TO: {email}")
    print(f"SUBJECT: {subject}")
    print(body)
    print("=" * 50)


def check_upcoming_notifications():

    print("\n[SYSTEM] Checking for tasks due in 48 hours...")

    response = requests.get(API_URL)

    employees = response.json()

    warning_date = (datetime.now() + timedelta(days=2)).date()

    for emp in employees:

        contract_end = datetime.fromisoformat(emp["contract_end"]).date()

        if contract_end == warning_date:

            assessor_email = "manager@company.com"

            send_notification(
                assessor_email,
                emp["name"],
                "Contract Evaluation",
                contract_end
            )


if __name__ == "__main__":
    check_upcoming_notifications()
