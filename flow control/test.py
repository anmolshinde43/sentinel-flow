from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler

from database import SessionLocal
from models import Employee


def check_probation_expiry():
    print(f"\n--- SCAN STARTED: {datetime.now().strftime('%H:%M:%S')} ---")

    db = SessionLocal()

    try:
        target_date = (datetime.now() + timedelta(days=14)).date()

        employees = db.query(Employee).filter(
            Employee.contract_end == target_date
        ).all()

        if employees:
            for emp in employees:
                emp.status = "Action Required"
                print(f"⚠️ ALERT: {emp.name}'s contract expires soon.")

            db.commit()

        else:
            print("No employees matching the 14-day rule.")

    finally:
        db.close()


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scheduler.add_job(check_probation_expiry, 'interval', seconds=15)

    print("Scheduler running...")

    scheduler.start()
