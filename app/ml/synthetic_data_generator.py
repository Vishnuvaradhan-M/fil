# app/ml/synthetic_data_generator.py

import random
from datetime import datetime, timedelta
from app.core.db import SessionLocal
from app.models.appointment import Appointment
from app.models.users import User


def seed_synthetic_data(days=90):

    db = SessionLocal()

    doctors = db.query(User).filter(User.role == "doctor").all()

    if not doctors:
        raise ValueError("Create doctors before seeding data.")

    base_date = datetime.now() - timedelta(days=days)

    for i in range(days):
        date = base_date + timedelta(days=i)

        for hour in range(9, 17):

            for _ in range(random.randint(5, 15)):

                appointment = Appointment(
                    patient_id=random.randint(1, 1000),
                    doctor_id=random.choice(doctors).id,
                    appointment_date=date.date(),
                    start_time=datetime.strptime(f"{hour}:00", "%H:%M").time(),
                    end_time=datetime.strptime(f"{hour+1}:00", "%H:%M").time(),
                    patient_name="Test Patient",
                    patient_phone="9999999999",
                    patient_gender="Male",
                    patient_age=random.randint(20, 70),
                    appointment_type=random.choice(["Consultation", "Emergency"]),
                    status="Completed",
                    reason_for_visit="General Checkup",
                )

                db.add(appointment)

    db.commit()
    db.close()
    print("Synthetic data seeded.")


if __name__ == "__main__":
    seed_synthetic_data()