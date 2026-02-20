from typing import Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from app.core import deps
from app.models.users import User, UserRole
from app.schemas import ml as schemas
from app.ml.forecast_service import ForecastService
from app.ml.feature_builder import FeatureBuilder

router = APIRouter()

# Singleton instance to avoid reloading model on each request
_forecast_service: ForecastService | None = None


def get_forecast_service() -> ForecastService:
    """Get or create singleton ForecastService instance."""
    global _forecast_service
    if _forecast_service is None:
        try:
            _forecast_service = ForecastService()
        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail="ML model not found. Please train the model first."
            )
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to load ML model: {str(e)}"
            )
    return _forecast_service


@router.post("/forecast", response_model=schemas.ForecastResponse)
def predict_demand(
    *,
    request: schemas.ForecastRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role([UserRole.ADMIN, UserRole.HR, UserRole.DOCTOR, UserRole.STAFF])),
) -> Any:
    """
    Predict appointment demand using ML model (All authenticated users).
    
    **Simplified Input**: Only date and hour required.
    All features (doctor_count, avg_patient_age, emergency_count) are 
    automatically extracted from database.
    
    **Returns**: Predicted demand with features used for transparency.
    """
    # Build features from database
    feature_builder = FeatureBuilder(db)
    
    try:
        features = feature_builder.build_features(request.date, request.hour)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract features from database: {str(e)}"
        )
    
    # Convert to DataFrame for ML service
    df = pd.DataFrame([features])
    
    # Get forecast service and make prediction
    service = get_forecast_service()
    
    try:
        predictions = service.predict(df)
        predicted_count = predictions[0]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
    
    # Return response with transparency
    return schemas.ForecastResponse(
        date=request.date,
        hour=request.hour,
        predicted_demand=predicted_count,
        features_used={
            "doctor_count": features["doctor_count"],
            "avg_patient_age": features["avg_patient_age"],
            "emergency_count": features["emergency_count"]
        }
    )


@router.post("/shift-optimize", response_model=schemas.ShiftOptimizeResponse)
def optimize_shift(
    *,
    request: schemas.ShiftOptimizeRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role([UserRole.ADMIN, UserRole.HR, UserRole.DOCTOR, UserRole.STAFF])),
) -> Any:
    """
    Get shift staffing recommendations based on predicted demand (All authenticated users).
    
    **Simplified Input**: Only date and hour required.
    - Forecast is called internally
    - Staff availability is fetched from database
    - Priority order is calculated automatically
    
    **Returns**: Optimized staff assignment with priority ranking.
    """
    # Step 1: Get forecast for this date/hour
    feature_builder = FeatureBuilder(db)
    
    try:
        features = feature_builder.build_features(request.date, request.hour)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract features: {str(e)}"
        )
    
    # Predict demand
    df = pd.DataFrame([features])
    service = get_forecast_service()
    
    try:
        predictions = service.predict(df)
        predicted_demand = predictions[0]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
    
    # Step 2: Get available staff from database
    try:
        # Map hour to shift type for potential future filtering
        if request.hour < 8:
            shift_type = "NIGHT"
        elif request.hour < 16:
            shift_type = "MORNING"
        else:
            shift_type = "AFTERNOON"
        
        available_staff = feature_builder.get_available_staff(
            target_date=request.date,
            shift_type=shift_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch staff: {str(e)}"
        )
    
    if not available_staff:
        raise HTTPException(
            status_code=404,
            detail="No staff available in database"
        )
    
    # Step 3: Calculate staffing needs (1 staff per 5-7 patients)
    recommended_count = max(1, int(predicted_demand / 5))
    
    # Step 4: Staff already sorted by SQL query (recent_assignments, monthly_assignments, name)
    # No additional sorting needed - just take top N
    assigned_staff = available_staff[:recommended_count]
    
    # Build response
    priority_order = [s["name"] for s in assigned_staff]
    
    staff_details = [
        schemas.StaffPriority(
            name=s["name"],
            current_assignments=s["recent_assignments"],  # Use recent assignments for display
            priority_rank=i + 1
        )
        for i, s in enumerate(assigned_staff)
    ]
    
    recommendation_text = (
        f"Assign {', '.join(priority_order)} based on predicted load of "
        f"{predicted_demand:.1f} patients. Staff prioritized by workload balance (7-day window + monthly fairness)."
    )
    
    return schemas.ShiftOptimizeResponse(
        date=request.date,
        hour=request.hour,
        predicted_demand=predicted_demand,
        recommended_staff_count=recommended_count,
        priority_order=priority_order,
        staff_details=staff_details,
        recommendation_text=recommendation_text
    )
