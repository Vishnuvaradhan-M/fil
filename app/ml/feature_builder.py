# app/ml/feature_builder.py
"""
Automatic feature extraction from database for ML predictions.
All features are derived from historical data - no manual inputs required.
"""

from datetime import date, time, datetime, timedelta
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.appointment import Appointment, DoctorAvailability
from app.models.shift import StaffShiftAssignment


class FeatureBuilder:
    """Extract ML features from database for a given date and hour."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def build_features(self, target_date: date, target_hour: int) -> Dict:
        """
        Build complete feature vector for ML model.
        
        Args:
            target_date: Date to predict for
            target_hour: Hour (0-23) to predict for
        
        Returns:
            Dictionary with all required ML features
        """
        features = {
            "appointment_date": datetime.combine(target_date, time(target_hour, 0)),
            "hour": target_hour,
            "doctor_count": self.get_doctor_count(target_date, target_hour),
            "avg_patient_age": self.get_avg_patient_age(target_date, target_hour),
            "emergency_count": self.get_emergency_count(target_date, target_hour),
        }
        
        return features
    
    def get_doctor_count(self, target_date: date, target_hour: int) -> int:
        """
        Count doctors available at the specified date and hour.
        Uses doctor_availability table.
        
        Args:
            target_date: Date to check
            target_hour: Hour to check (0-23)
        
        Returns:
            Number of doctors available
        """
        day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
        target_time = time(target_hour, 0)
        
        # Query doctor_availability for matching day and time
        count = self.db.query(DoctorAvailability).filter(
            and_(
                DoctorAvailability.day_of_week == day_of_week,
                DoctorAvailability.start_time <= target_time,
                DoctorAvailability.end_time > target_time
            )
        ).count()
        
        # Default to 2 if no availability data
        return max(count, 2)
    
    def get_avg_patient_age(self, target_date: date, target_hour: int) -> float:
        """
        Calculate average patient age from historical appointments.
        Uses data from same hour over last 60 days or same weekday over last 8 weeks.
        
        Args:
            target_date: Date to predict for
            target_hour: Hour to predict for
        
        Returns:
            Average patient age (default 40.0 if no data)
        """
        # Strategy 1: Last 60 days, same hour range
        start_date = target_date - timedelta(days=60)
        
        # Query appointments in same hour window
        avg_age = self.db.query(func.avg(Appointment.patient_age)).filter(
            and_(
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date < target_date,
                func.extract('hour', Appointment.start_time) == target_hour
            )
        ).scalar()
        
        if avg_age:
            return float(avg_age)
        
        # Strategy 2: Same weekday, last 8 weeks
        weekday = target_date.weekday()
        past_dates = [target_date - timedelta(weeks=i) for i in range(1, 9)]
        
        avg_age = self.db.query(func.avg(Appointment.patient_age)).filter(
            and_(
                Appointment.appointment_date.in_(past_dates),
                func.extract('hour', Appointment.start_time) == target_hour
            )
        ).scalar()
        
        if avg_age:
            return float(avg_age)
        
        # Default fallback
        return 40.0
    
    def get_emergency_count(self, target_date: date, target_hour: int) -> int:
        """
        Count emergency appointments in the past hour from historical data.
        Uses appointment_type = 'EMERGENCY' (or 'Emergency').
        
        Args:
            target_date: Date to check
            target_hour: Hour to check
        
        Returns:
            Number of emergencies in similar time slots (default 1)
        """
        # Look at last 30 days for same hour
        start_date = target_date - timedelta(days=30)
        
        # Count emergencies in same hour over past 30 days
        emergency_count = self.db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date < target_date,
                func.extract('hour', Appointment.start_time) == target_hour,
                or_(
                    Appointment.appointment_type == 'EMERGENCY',
                    Appointment.appointment_type == 'Emergency'
                )
            )
        ).scalar()
        
        if emergency_count:
            # Average per day
            days_span = min((target_date - start_date).days, 30)
            avg_per_day = emergency_count / max(days_span, 1)
            return max(int(avg_per_day), 1)
        
        # Default assuming some emergency load
        return 1
    
    def get_available_staff(self, target_date: date, shift_type: str = None):
        """
        Get available staff with rolling workload window (7 days + current).
        
        Uses:
        - 7-day lookback for recent workload
        - Monthly assignments for fairness
        - Deterministic alphabetical fallback
        
        Args:
            target_date: Date to check
            shift_type: Shift type (MORNING/AFTERNOON/NIGHT) - currently unused
        
        Returns:
            List of staff dictionaries sorted by workload (fairest first)
        """
        from sqlalchemy import text
        
        query = """
        SELECT
            u.id AS staff_id,
            u.full_name,
            
            -- Workload in last 7 days (including target date)
            COUNT(
                CASE
                    WHEN DATE(s.start_time) BETWEEN
                         :target_date - INTERVAL '7 days'
                         AND :target_date
                    THEN 1
                END
            ) AS recent_assignments,
            
            -- Workload in same calendar month (fairness metric)
            COUNT(
                CASE
                    WHEN DATE_TRUNC('month', s.start_time)
                         = DATE_TRUNC('month', CAST(:target_date AS DATE))
                    THEN 1
                END
            ) AS monthly_assignments
        
        FROM users u
        LEFT JOIN staff_shift_assignments ssa
            ON u.id = ssa.staff_id
        LEFT JOIN shifts s
            ON ssa.shift_id = s.id
        
        WHERE u.role IN ('DOCTOR', 'STAFF')
          AND u.is_active = true
        
        GROUP BY u.id, u.full_name
        
        ORDER BY
            recent_assignments ASC,
            monthly_assignments ASC,
            u.full_name ASC;
        """
        
        result = self.db.execute(
            text(query),
            {"target_date": target_date}
        ).mappings().all()
        
        return [
            {
                "staff_id": row["staff_id"],
                "name": row["full_name"],
                "current_assignments": row["recent_assignments"],
                "recent_assignments": row["recent_assignments"],
                "monthly_assignments": row["monthly_assignments"]
            }
            for row in result
        ]
