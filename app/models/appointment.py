from sqlalchemy import Column, Integer, String, DateTime, Date, Time, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base
import enum


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    NO_SHOW = "NoShow"


class PatientGender(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class AppointmentType(str, enum.Enum):
    CONSULTATION = "Consultation"
    FOLLOW_UP = "Follow-up"
    REVIEW = "Review"
    EMERGENCY = "Emergency"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Administrative scheduling fields
    appointment_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    patient_name = Column(String(120), nullable=False)
    patient_phone = Column(String(20), nullable=False)
    patient_email = Column(String(255), nullable=True)
    patient_gender = Column(Enum(PatientGender), nullable=False)
    patient_age = Column(Integer, nullable=False)

    appointment_type = Column(Enum(AppointmentType), nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    reason_for_visit = Column(String(255), nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    doctor = relationship("User", backref="appointments")


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"

    id= Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    doctor = relationship("User", backref="availabilities")
