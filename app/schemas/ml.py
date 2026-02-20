from typing import List
from datetime import date as DateType
from pydantic import BaseModel, Field


# Forecast Schemas (Simplified - Auto-extract features from DB)
class ForecastRequest(BaseModel):
    """Request schema for demand forecasting - date and hour only."""
    date: DateType = Field(..., description="Date for forecast (YYYY-MM-DD)")
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")


class ForecastResponse(BaseModel):
    """Response schema for demand forecasting."""
    date: DateType = Field(..., description="Requested date")
    hour: int = Field(..., description="Requested hour")
    predicted_demand: float = Field(..., description="Predicted number of appointments")
    features_used: dict = Field(..., description="Features extracted from database")


# Shift Optimization Schemas (Simplified - Auto-fetch staff from DB)
class ShiftOptimizeRequest(BaseModel):
    """Request schema for shift optimization - date and hour only."""
    date: DateType = Field(..., description="Date for shift planning (YYYY-MM-DD)")
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")


class StaffPriority(BaseModel):
    """Individual staff member with priority info."""
    name: str = Field(..., description="Staff member name")
    current_assignments: int = Field(..., description="Current workload")
    priority_rank: int = Field(..., description="Assignment priority (1=highest)")


class ShiftOptimizeResponse(BaseModel):
    """Response schema for shift optimization."""
    date: DateType = Field(..., description="Requested date")
    hour: int = Field(..., description="Requested hour")
    predicted_demand: float = Field(..., description="Predicted patient demand")
    recommended_staff_count: int = Field(..., description="Recommended number of staff")
    priority_order: List[str] = Field(..., description="Staff names in priority order")
    staff_details: List[StaffPriority] = Field(..., description="Detailed staff information")
    recommendation_text: str = Field(..., description="Human-readable recommendation")

