import json
import requests
from datetime import datetime, timedelta

# Load workflow templates from JSON files
with open("software_intern.json") as f:
    software_template = json.load(f)

with open("factory_intern.json") as f:
    factory_template = json.load(f)

ROLE_TEMPLATES = {
    software_template["role"]: software_template["milestones"],
    factory_template["role"]: factory_template["milestones"]
}

# FastAPI endpoint
API_URL = "http://127.0.0.1:8000/employees"


def add_employee_and_generate_workflow(name, role, start_date_str):

    print(f"\n[SYSTEM] Adding new {role}: {name}")

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

    # Example: contract ends in 6 months
    contract_end = (start_date + timedelta(days=180)).date().isoformat()

    # Send employee to your backend API
    employee_data = {
        "name": name,
        "email": f"{name.lower().replace(' ', '.')}@company.com",
        "role": role,
        "salary": 20000,
        "manager_id": None,
        "contract_start": start_date_str,
        "contract_end": contract_end
    }

    response = requests.post(API_URL, json=employee_data)

    if response.status_code != 200:
        print("❌ Failed to create employee")
        print(response.text)
        return

    employee = response.json()

    print(f"✅ Employee created in database with ID: {employee['id']}")

    # Generate workflow milestones
    template = ROLE_TEMPLATES.get(role)

    if template:

        print(f"[ORCHESTRATOR] Generating {len(template)} milestones...")

        for step in template:

            due_date = (start_date + timedelta(days=step["offset_days"])).date()

            print(
                f" -> Scheduled: {step['task']} "
                f"for {due_date} "
                f"(Assigned to {step['assigned_to']})"
            )

    else:
        print("[ERROR] No workflow template found for role")


# --- RUN DEMO ---
if __name__ == "__main__":

    # Example 1
    add_employee_and_generate_workflow(
        "Meeth",
        "Software Intern",
        "2026-03-01"
    )

    # Example 2
    add_employee_and_generate_workflow(
        "John Doe",
        "Factory Intern",
        "2026-03-01"
    )
