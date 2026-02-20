# app/ml/dataset_builder.py

from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from app.core.db import SessionLocal
from app.models.appointment import Appointment
from app.models.users import User
import pandas as pd


def build_ml_dataset() -> pd.DataFrame:
    db: Session = SessionLocal()

    query = (
        db.query(
            Appointment.appointment_date.label("appointment_date"),
            extract("hour", Appointment.start_time).label("hour"),
            func.count(Appointment.id).label("appointment_count"),
            func.count(func.distinct(Appointment.doctor_id)).label("doctor_count"),
            func.avg(Appointment.patient_age).label("avg_patient_age"),
            func.sum(
                case(
                    (Appointment.appointment_type == "Emergency", 1),
                    else_=0
                )
            ).label("emergency_count"),
        )
        .group_by(
            Appointment.appointment_date,
            extract("hour", Appointment.start_time)
        )
        .order_by(Appointment.appointment_date)
    )

    df = pd.read_sql(query.statement, db.bind)

    if df.empty:
        raise ValueError("Dataset is empty. Please seed data first.")

    df["appointment_date"] = pd.to_datetime(df["appointment_date"])
    db.close()

    return df