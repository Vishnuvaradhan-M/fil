# Import all models so Base.metadata.create_all() picks them up
from app.models.users import User, UserRole  # noqa: F401
from app.models.appointment import Appointment, DoctorAvailability  # noqa: F401
from app.models.room import Room  # noqa: F401  (OTSlot, OTBooking commented out until schema aligned)
from app.models.shift import Shift, StaffShiftAssignment  # noqa: F401
