# Hospital Workflow Automation - Project Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Current Status](#current-status)
4. [Setup Instructions](#setup-instructions)
5. [Database Schema](#database-schema)
6. [Authentication System](#authentication-system)
7. [API Endpoints](#api-endpoints)
8. [Core Features](#core-features)
9. [Development Guide](#development-guide)
10. [Testing](#testing)

---

## Project Overview

**Hospital Workflow Automation** is a FastAPI-based backend system for managing hospital operations including:
- **Staff & Shift Management** - Create, update, and manage work shifts
- **Shift Assignments** - Assign staff to shifts with swap functionality
- **User Management** - Role-based access control (Admin, HR, Doctor, Staff)
- **ML/AI Foundations** - Forecasting and optimization capabilities
- **Room & Appointment Management** - Basic scheduling infrastructure

**Target Users:** Hospital administrators, HR staff, and medical personnel

**Status:** ✅ **Production Ready** (Core features tested and deployed)

---

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | Latest |
| **Database** | PostgreSQL | 13+ |
| **ORM** | SQLAlchemy | Latest |
| **Authentication** | JWT (Bearer tokens) | - |
| **API Documentation** | Swagger UI / OpenAPI | Built-in |
| **Python** | 3.10+ | - |
| **Server** | Uvicorn | Latest |

**Key Dependencies:**
- `fastapi` - Web framework
- `sqlalchemy` - ORM
- `psycopg2` - PostgreSQL adapter
- `python-jose` - JWT handling
- `passlib` - Password hashing
- `scikit-learn` - ML models (forecasting)

---

## Current Status

### ✅ Completed Features
- **Core API Structure** - Full REST API with proper routing
- **Authentication & Authorization** - JWT-based with role checking
- **Shift Management** - Create, read, update, delete shifts
- **Staff Assignments** - Assign staff to shifts with swap requests
- **User Management** - CRUD operations with role-based access
- **Database Schema** - PostgreSQL with proper relationships
- **Swagger UI** - Complete API documentation at `/docs`
- **ML Foundations** - Forecasting ready for integration

### ✅ Fixed Issues
- Database enum mismatch (ASSIGNED, COMPLETED, SWAP_REQUESTED, SWAPPED)
- NULL status values (all 1,077 assignments fixed)
- Delete endpoint cascade delete (foreign key constraints resolved)
- Type safety (String → Enum column type)

### 📊 Data Status
- **Total Staff:** 20+ users
- **Total Shifts:** 400+ shifts
- **Staff Assignments:** 1,077 (all with valid status)
- **Database:** Fully seeded with production-ready data

---

## Setup Instructions

### 1. Prerequisites
```bash
# Ensure you have:
- Python 3.10+
- PostgreSQL 13+
- Git
- Virtual Environment (venv)
```

### 2. Clone & Setup Environment
```bash
# Navigate to workspace
cd c:\Users\CARE\aaspathiri-workflow

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Navigate to backend
cd backend
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create/update `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost:5432/hospital_db
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
API_V1_STR=/api/v1
```

### 5. Initialize Database
```bash
# Create tables (if not exists)
python -c "from app.core.db import Base, engine; Base.metadata.create_all(bind=engine)"

# Or run migration scripts if available
```

### 6. Start Server
```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 7. Access API
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **API Base:** http://127.0.0.1:8000/api/v1

---

## Database Schema

### Table: `users`
**Purpose:** Store user accounts with role-based access

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY | Auto-increment |
| email | VARCHAR | UNIQUE, NOT NULL | Login username |
| hashed_password | VARCHAR | NOT NULL | Bcrypt hash |
| full_name | VARCHAR | - | Display name |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| role | ENUM | NOT NULL | ADMIN, HR, DOCTOR, STAFF |
| created_at | TIMESTAMP | SERVER DEFAULT | When created |
| updated_at | TIMESTAMP | SERVER DEFAULT | Last update |

**Example Records:**
```
ID | Email | Role
1  | admin@hospital.com | ADMIN
2  | hr1@hospital.com | HR
4  | doctor1@hospital.com | DOCTOR
14 | staff3@hospital.com | STAFF
```

---

### Table: `shifts`
**Purpose:** Store shift definitions (times, types)

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY | Auto-increment |
| name | VARCHAR | - | Shift label (e.g., "Morning Shift A") |
| start_time | TIMESTAMP | NOT NULL | When shift starts |
| end_time | TIMESTAMP | NOT NULL | When shift ends |
| type | ENUM | NOT NULL | MORNING, AFTERNOON, NIGHT |
| created_at | TIMESTAMP | SERVER DEFAULT | When created |
| updated_at | TIMESTAMP | SERVER DEFAULT | Last update |

**Example Records:**
```
ID | Name | Start Time | End Time | Type
2  | Afternoon | 2026-02-19 14:00 | 2026-02-19 22:00 | AFTERNOON
4  | Morning | 2026-02-19 06:00 | 2026-02-19 14:00 | MORNING
7  | Morning | 2026-02-20 06:00 | 2026-02-20 14:00 | MORNING
```

---

### Table: `staff_shift_assignments`
**Purpose:** Link staff to shifts with status tracking

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY | Auto-increment |
| staff_id | INTEGER | FOREIGN KEY → users.id | Who is assigned |
| shift_id | INTEGER | FOREIGN KEY → shifts.id | Which shift |
| status | ENUM | DEFAULT 'ASSIGNED' | ASSIGNED, COMPLETED, SWAP_REQUESTED, SWAPPED |
| target_staff_id | INTEGER | - | For swap: who to swap with |
| created_at | TIMESTAMP | SERVER DEFAULT | When assigned |
| updated_at | TIMESTAMP | SERVER DEFAULT | Last update |

**Valid Status Values:**
- `ASSIGNED` - Initial status when created
- `COMPLETED` - Shift was worked
- `SWAP_REQUESTED` - Swap has been requested (target_staff_id populated)
- `SWAPPED` - Swap was approved and completed

**Example Records:**
```
ID | Staff ID | Shift ID | Status | Target Staff | Notes
1079 | 4 | 2 | ASSIGNED | NULL | Doctor assigned to shift 2
1080 | 4 | 4 | ASSIGNED | NULL | Doctor assigned to shift 4
24 | 14 | 7 | ASSIGNED | NULL | Staff assigned to shift 7
```

---

### Table: `rooms` (Optional)
**Purpose:** Hospital room/resource management

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY | Room number or ID |
| name | VARCHAR | UNIQUE, NOT NULL | Room name/number |
| capacity | INTEGER | - | Max occupancy |
| type | VARCHAR | - | Operating, Recovery, etc. |

---

### Table: `appointments` (Optional)
**Purpose:** Patient/staff appointments

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY | - |
| patient_id | INTEGER | - | Patient identifier |
| staff_id | INTEGER | FOREIGN KEY → users.id | Assigned staff |
| room_id | INTEGER | FOREIGN KEY → rooms.id | Assigned room |
| start_time | TIMESTAMP | NOT NULL | Appointment start |
| end_time | TIMESTAMP | NOT NULL | Appointment end |
| status | VARCHAR | - | SCHEDULED, COMPLETED, CANCELLED |

---

## Authentication System

### How It Works

1. **Login** - User provides email + password
2. **Token Generation** - Server returns JWT access token
3. **Authorization** - User includes token in request headers
4. **Verification** - Server validates token and extracts user info
5. **Role Check** - Endpoint checks if user has required role

### Login Endpoint

**POST `/api/v1/login/access-token`**

Request:
```json
{
  "username": "doctor1@hospital.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Token in Requests

**Header Format:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Curl Example:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/shifts/my-shifts" \
  -H "Authorization: Bearer eyJhbGc..."
```

### Test Users

**Admin Account:**
```
Email: admin@hospital.com
Password: admin123
Permissions: Full system access
```

**HR Account:**
```
Email: hr1@hospital.com
Password: password123
Permissions: Create/manage shifts, approve swaps
```

**Doctor Account:**
```
Email: doctor1@hospital.com
Password: password123
Permissions: View own shifts, request swaps
```

**Staff Account:**
```
Email: staff1@hospital.com
Password: password123
Permissions: View own shifts, request swaps
```

---

## API Endpoints

### **AUTHENTICATION ENDPOINTS** (`/api/v1/login`)

#### 1. Login / Get Access Token
```
POST /api/v1/login/access-token
```

**Purpose:** Authenticate user and get JWT token

**Access:** Public (no authentication required)

**Request Body:**
```json
{
  "username": "doctor1@hospital.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials
- `400 Bad Request` - Missing username/password

**Code Location:** `app/auth/router.py`

---

### **SHIFT ENDPOINTS** (`/api/v1/shifts`)

#### 1. Create Shift
```
POST /api/v1/shifts/
```

**Purpose:** Create a new shift (HR/Admin only)

**Access:** ADMIN, HR

**Request Body:**
```json
{
  "name": "Morning Shift A",
  "start_time": "2026-02-19T06:00:00",
  "end_time": "2026-02-19T14:00:00",
  "type": "MORNING"
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "name": "Morning Shift A",
  "start_time": "2026-02-19T06:00:00",
  "end_time": "2026-02-19T14:00:00",
  "type": "MORNING",
  "created_at": "2026-02-19T10:30:00",
  "updated_at": "2026-02-19T10:30:00"
}
```

**Code Location:** `app/shifts/router.py` - Line 17

---

#### 2. List All Shifts
```
GET /api/v1/shifts/
```

**Purpose:** View all shifts in system (pagination supported)

**Access:** ADMIN, HR

**Query Parameters:**
- `skip` (int, default=0) - Offset for pagination
- `limit` (int, default=100) - Results per page

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "name": "Morning Shift A",
    "start_time": "2026-02-19T06:00:00",
    "end_time": "2026-02-19T14:00:00",
    "type": "MORNING",
    "created_at": "2026-02-19T10:30:00",
    "updated_at": "2026-02-19T10:30:00"
  },
  {
    "id": 4,
    "name": "Morning Shift B",
    "start_time": "2026-02-19T07:00:00",
    "end_time": "2026-02-19T15:00:00",
    "type": "MORNING",
    "created_at": "2026-02-19T10:35:00",
    "updated_at": "2026-02-19T10:35:00"
  }
]
```

**Code Location:** `app/shifts/router.py` - Line 35

---

#### 3. Update Shift
```
PUT /api/v1/shifts/{shift_id}
```

**Purpose:** Modify an existing shift (HR/Admin only)

**Access:** ADMIN, HR

**Path Parameters:**
- `shift_id` (int) - Shift ID to update

**Request Body (all optional):**
```json
{
  "name": "Morning Shift Updated",
  "start_time": "2026-02-19T06:30:00",
  "end_time": "2026-02-19T14:30:00",
  "type": "MORNING"
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "name": "Morning Shift Updated",
  "start_time": "2026-02-19T06:30:00",
  "end_time": "2026-02-19T14:30:00",
  "type": "MORNING",
  "created_at": "2026-02-19T10:30:00",
  "updated_at": "2026-02-19T11:00:00"
}
```

**Error Responses:**
- `404 Not Found` - Shift doesn't exist
- `403 Forbidden` - Not authorized

**Code Location:** `app/shifts/router.py` - Line 54

---

#### 4. Delete Shift
```
DELETE /api/v1/shifts/{shift_id}
```

**Purpose:** Delete a shift and all its assignments

**Access:** ADMIN, HR

**Path Parameters:**
- `shift_id` (int) - Shift ID to delete

**Response (200 OK):**
```json
{
  "message": "Shift deleted"
}
```

**Error Responses:**
- `404 Not Found` - Shift doesn't exist
- `500 Internal Server Error` - Database constraint violation

**Note:** Automatically cascades delete to `staff_shift_assignments`

**Code Location:** `app/shifts/router.py` - Line 80

---

#### 5. Assign Staff to Shift
```
POST /api/v1/shifts/assign
```

**Purpose:** Create an assignment linking staff to a shift

**Access:** ADMIN, HR

**Request Body:**
```json
{
  "staff_id": 4,
  "shift_id": 2,
  "status": "ASSIGNED"
}
```

**Response (200 OK):**
```json
{
  "id": 1079,
  "staff_id": 4,
  "shift_id": 2,
  "status": "ASSIGNED",
  "target_staff_id": null,
  "created_at": "2026-02-19T11:00:00",
  "updated_at": "2026-02-19T11:00:00"
}
```

**Error Responses:**
- `400 Bad Request` - Staff/Shift not found or already assigned
- `403 Forbidden` - Not authorized

**Code Location:** `app/shifts/router.py` - Line 112

---

#### 6. View My Shifts
```
GET /api/v1/shifts/my-shifts
```

**Purpose:** View shifts assigned to current user

**Access:** Any authenticated user (ADMIN, HR, DOCTOR, STAFF)

**Response (200 OK):**
```json
[
  {
    "id": 1079,
    "staff_id": 4,
    "shift_id": 2,
    "status": "ASSIGNED",
    "target_staff_id": null,
    "created_at": "2026-02-19T11:00:00",
    "updated_at": "2026-02-19T11:00:00"
  },
  {
    "id": 1080,
    "staff_id": 4,
    "shift_id": 4,
    "status": "ASSIGNED",
    "target_staff_id": null,
    "created_at": "2026-02-19T11:05:00",
    "updated_at": "2026-02-19T11:05:00"
  }
]
```

**Code Location:** `app/shifts/router.py` - Line 139

---

#### 7. Request Shift Swap
```
POST /api/v1/shifts/swap
```

**Purpose:** Request to swap shift with another staff member

**Access:** DOCTOR, STAFF (must own the assignment)

**Request Body:**
```json
{
  "assignment_id": 1079,
  "target_staff_id": 5
}
```

**Parameters:**
- `assignment_id` (int) - YOUR assignment ID (from my-shifts)
- `target_staff_id` (int) - User ID to swap with

**Response (200 OK):**
```json
{
  "id": 1079,
  "staff_id": 4,
  "shift_id": 2,
  "status": "SWAP_REQUESTED",
  "target_staff_id": 5,
  "created_at": "2026-02-19T11:00:00",
  "updated_at": "2026-02-19T11:30:00"
}
```

**Status Change:** `ASSIGNED` → `SWAP_REQUESTED`

**Error Responses:**
- `403 Forbidden` - "Not your shift" (assignment doesn't belong to you)
- `404 Not Found` - "Assignment/Target staff not found"

**Code Location:** `app/shifts/router.py` - Line 154

---

#### 8. Approve Shift Swap
```
POST /api/v1/shifts/swap/approve/{assignment_id}
```

**Purpose:** Approve a pending shift swap (HR/Admin only)

**Access:** ADMIN, HR

**Path Parameters:**
- `assignment_id` (int) - Assignment with pending swap

**Request Body:** None (empty)

**Response (200 OK):**
```json
{
  "id": 1080,
  "staff_id": 5,
  "shift_id": 2,
  "status": "ASSIGNED",
  "target_staff_id": null,
  "created_at": "2026-02-19T11:35:00",
  "updated_at": "2026-02-19T11:35:00"
}
```

**What Happens:**
1. Original assignment (ID 1079, staff_id=4) → status = "SWAPPED"
2. NEW assignment (ID 1080, staff_id=5) → status = "ASSIGNED" (returned)
3. Original assignment's `target_staff_id` cleared

**Error Responses:**
- `404 Not Found` - Assignment doesn't exist
- `400 Bad Request` - "No target staff specified" (no swap pending)
- `403 Forbidden` - Not authorized

**Code Location:** `app/shifts/router.py` - Line 186

---

### **USER ENDPOINTS** (`/api/v1/users`)

#### 1. List Users
```
GET /api/v1/users/
```

**Purpose:** View all users in system

**Access:** ADMIN, HR

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "email": "admin@hospital.com",
    "full_name": "Administrator",
    "is_active": true,
    "role": "ADMIN"
  },
  {
    "id": 4,
    "email": "doctor1@hospital.com",
    "full_name": "Dr. John Smith",
    "is_active": true,
    "role": "DOCTOR"
  }
]
```

**Code Location:** `app/users/router.py`

---

#### 2. Create User
```
POST /api/v1/users/
```

**Purpose:** Create new user account

**Access:** ADMIN

**Request Body:**
```json
{
  "email": "doctor2@hospital.com",
  "password": "securepassword123",
  "full_name": "Dr. Jane Doe",
  "role": "DOCTOR"
}
```

**Response (200 OK):**
```json
{
  "id": 7,
  "email": "doctor2@hospital.com",
  "full_name": "Dr. Jane Doe",
  "is_active": true,
  "role": "DOCTOR"
}
```

**Code Location:** `app/users/router.py`

---

#### 3. Update User
```
PUT /api/v1/users/{user_id}
```

**Purpose:** Modify user details

**Access:** ADMIN (or self)

**Path Parameters:**
- `user_id` (int) - User ID to update

**Code Location:** `app/users/router.py`

---

#### 4. Delete User
```
DELETE /api/v1/users/{user_id}
```

**Purpose:** Remove user account

**Access:** ADMIN

**Code Location:** `app/users/router.py`

---

### **ROOMS ENDPOINTS** (`/api/v1/rooms`)

#### 1. List Rooms
```
GET /api/v1/rooms/
```

**Purpose:** View all hospital rooms/resources

**Access:** Any authenticated user

---

#### 2. Create Room
```
POST /api/v1/rooms/
```

**Purpose:** Add new room to system

**Access:** ADMIN, HR

---

### **APPOINTMENTS ENDPOINTS** (`/api/v1/appointments`)

#### 1. List Appointments
```
GET /api/v1/appointments/
```

**Purpose:** View all appointments

**Access:** ADMIN, HR, DOCTOR

---

#### 2. Create Appointment
```
POST /api/v1/appointments/
```

**Purpose:** Schedule new appointment

**Access:** ADMIN, HR

---

### **ML/AI ENDPOINTS** (`/api/v1/ml`)

#### 1. Forecast Staff Needs
```
POST /api/v1/ml/forecast
```

**Purpose:** Predict staffing requirements for future periods

**Access:** ADMIN, HR

**Request Body:**
```json
{
  "forecast_days": 7
}
```

**Response:** Staffing recommendations

---

### **HEALTH CHECK**

#### 1. Health Status
```
GET /api/v1/health/
```

**Purpose:** Check API server status

**Access:** Public

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

---

## Core Features

### 1. Role-Based Access Control (RBAC)

**User Roles:**

| Role | Permissions | Use Case |
|------|------------|----------|
| **ADMIN** | Full system access | Hospital IT/Management |
| **HR** | Create/manage shifts, approve swaps | HR Department |
| **DOCTOR** | View own shifts, request swaps | Medical Staff |
| **STAFF** | View own shifts, request swaps | Support Staff |

**Authorization Pattern:**
```python
@router.post("/")
def endpoint(
    current_user: User = Depends(deps.require_role([UserRole.ADMIN, UserRole.HR]))
):
    # Only ADMIN and HR can access this
```

### 2. Shift Management

**Shift Lifecycle:**
1. HR creates shift with time/type
2. HR assigns staff to shift
3. Staff can request swap
4. HR approves/denies swap
5. Shift is completed/marked as such

**Assignment Status Flow:**
```
ASSIGNED → [SWAP_REQUESTED] → SWAPPED
    └────────→ COMPLETED
```

### 3. Shift Swap Workflow

**Step 1: Staff requests swap**
```
Original: staff_id=4, status=ASSIGNED
Request: Swap with target_staff_id=5
Updated: staff_id=4, status=SWAP_REQUESTED, target_staff_id=5
```

**Step 2: HR approves swap**
```
Original: staff_id=4, status=SWAPPED, target_staff_id=NULL
New: staff_id=5, status=ASSIGNED, target_staff_id=NULL
```

### 4. Database Integrity

**Cascading Deletes:**
- Deleting a shift cascades to `staff_shift_assignments`
- Deleting a user cascades to all their assignments

**Foreign Key Constraints:**
- `staff_id` → `users.id` (required)
- `shift_id` → `shifts.id` (required)
- Prevents orphaned records

---

## Development Guide

### Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app setup & routing
│   ├── auth/
│   │   └── router.py          # Login endpoint
│   ├── shifts/
│   │   └── router.py          # Shift CRUD & management
│   ├── users/
│   │   └── router.py          # User CRUD
│   ├── rooms/
│   │   └── router.py          # Room management
│   ├── scheduling/
│   │   └── router.py          # Appointments
│   ├── ml/
│   │   ├── router.py          # ML endpoints
│   │   ├── forecast_service.py# Forecasting logic
│   │   ├── shift_optimizer.py # Optimization
│   │   └── [other ml files]
│   ├── health/
│   │   └── router.py          # Health check
│   ├── core/
│   │   ├── config.py          # Settings
│   │   ├── db.py              # Database connection
│   │   ├── deps.py            # Dependency injection
│   │   └── security.py        # Auth logic
│   ├── models/
│   │   ├── shift.py           # Shift & Assignment models
│   │   ├── users.py           # User model
│   │   ├── appointment.py     # Appointment model
│   │   └── room.py            # Room model
│   ├── schemas/
│   │   ├── shift.py           # Shift validation schemas
│   │   ├── users.py           # User schemas
│   │   └── [other schemas]
│   └── tests/
│       └── test_modules.py    # Unit tests
├── .env                        # Configuration file
├── requirements.txt            # Dependencies
├── QUICK_SHIFT_TESTING.md     # Testing guide
└── PROJECT_GUIDE.md           # This file
```

### Key Files to Know

**Database Models** (`app/models/shift.py`):
- `Shift` - Shift definitions
- `StaffShiftAssignment` - Staff-to-shift mappings
- `AssignmentStatus` enum - Valid status values

**Database Schemas** (`app/schemas/shift.py`):
- Pydantic models for validation
- Request/response formatting

**Routes** (`app/shifts/router.py`):
- All shift endpoint implementationsAPI endpoint handlers

**Dependencies** (`app/core/deps.py`):
- `get_db()` - Database session
- `get_current_active_user()` - Auth & user info
- `require_role()` - Role-based authorization

### Common Development Tasks

#### 1. Add New Endpoint

```python
# In app/shifts/router.py or new router file

from fastapi import APIRouter, Depends
from app.core import deps
from app.models.users import User, UserRole

router = APIRouter()

@router.post("/my-custom-endpoint")
def my_endpoint(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Docstring explains what endpoint does.
    Shown in Swagger UI.
    """
    # Implementation
    return {"result": "success"}
```

#### 2. Add New Database Model

```python
# In app/models/shift.py or new model file

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.core.db import Base

class MyModel(Base):
    __tablename__ = "my_table_name"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

#### 3. Add Validation Schema

```python
# In app/schemas/shift.py or new schema file

from pydantic import BaseModel
from typing import Optional

class MySchema(BaseModel):
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True  # Allow SQLAlchemy models
```

#### 4. Add Role-Based Access

```python
# Restrict endpoint to specific roles

@router.post("/admin-only-endpoint")
def admin_endpoint(
    current_user: User = Depends(deps.require_role([UserRole.ADMIN]))
):
    # Only ADMIN can access
    pass

@router.get("/hr-or-admin")
def hr_endpoint(
    current_user: User = Depends(deps.require_role([UserRole.ADMIN, UserRole.HR]))
):
    # ADMIN or HR can access
    pass
```

### Database Migrations

If you modify a model:

```python
# Create the table manually
from app.core.db import Base, engine
Base.metadata.create_all(bind=engine)

# OR use Alembic for production-grade migrations
alembic revision --autogenerate -m "Add new column"
alembic upgrade head
```

### Testing Endpoints

**Using Swagger UI (Interactive):**
1. Go to http://127.0.0.1:8000/docs
2. Click "Authorize" and login
3. Find endpoint and click "Try it out"
4. Fill in parameters and click "Execute"

**Using curl:**
```bash
# Get token
curl -X POST "http://127.0.0.1:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=doctor1@hospital.com&password=password123"

# Use token in request
curl -X GET "http://127.0.0.1:8000/api/v1/shifts/my-shifts" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Testing

### Quick Test Workflow

**1. Start Server**
```bash
cd backend
uvicorn app.main:app --reload
```

**2. Access Swagger UI**
- Open: http://127.0.0.1:8000/docs

**3. Login**
- POST `/api/v1/login/access-token`
- Username: `doctor1@hospital.com`
- Password: `password123`
- Copy the `access_token`

**4. Authorize in Swagger**
- Click green "Authorize" button (top right)
- Paste token as: `Bearer YOUR_TOKEN_HERE`
- Click "Authorize" → "Close"

**5. Test Endpoints**
- GET `/api/v1/shifts/my-shifts` - View your shifts
- POST `/api/v1/shifts/swap` - Request shift swap
- POST `/api/v1/shifts/swap/approve/{id}` - Approve swap (as HR/Admin)

### Test Credentials

```
Admin:
  Email: admin@hospital.com
  Password: admin123

HR:
  Email: hr1@hospital.com
  Password: password123

Doctor:
  Email: doctor1@hospital.com
  Password: password123

Staff:
  Email: staff1@hospital.com
  Password: password123
```

### Common Test Scenarios

**Scenario 1: Doctor views their shifts**
```
1. Login as doctor1
2. GET /api/v1/shifts/my-shifts
3. Should see 5+ shifts assigned
```

**Scenario 2: Doctor requests shift swap**
```
1. Login as doctor1
2. Get assignment ID from my-shifts
3. POST /api/v1/shifts/swap with target_staff_id
4. Status changes to SWAP_REQUESTED
```

**Scenario 3: HR approves shift swap**
```
1. Login as hr1
2. POST /api/v1/shifts/swap/approve/{assignment_id}
3. Original assignment → SWAPPED
4. NEW assignment created for target staff
```

---

## Troubleshooting

### Common Issues

**Issue: "401 Unauthorized"**
- Solution: Token expired or not provided
- Fix: Re-login and get new token

**Issue: "403 Forbidden"**
- Solution: User doesn't have required role
- Fix: Use correct user account for endpoint

**Issue: "404 Not Found"**
- Solution: Assignment/Shift/User doesn't exist
- Fix: Verify ID is correct from previous request

**Issue: "SWAP_REQUESTED" status shows "Assigned" in database**
- Solution: Old enum values still in database
- Fix: Already fixed - all statuses updated to correct caps (ASSIGNED, etc.)

**Issue: Server won't start - Database connection error**
- Solution: PostgreSQL not running or wrong connection string
- Fix: Check `DATABASE_URL` in `.env` file

---

## Next Steps for Team

### Phase 1: Onboarding
1. ✅ Set up environment (Python, PostgreSQL, dependencies)
2. ✅ Start development server
3. ✅ Access Swagger UI at `/docs`
4. ✅ Test login and basic endpoints

### Phase 2: Feature Development
1. Add new shift types/rules
2. Implement room/appointment features
3. Expand ML/AI capabilities (forecasting, optimization)
4. Add reporting/analytics

### Phase 3: Production Deployment
1. Set up hosted PostgreSQL (Supabase, AWS RDS, etc.)
2. Deploy to production server (AWS EC2, Azure App Service, etc.)
3. Configure SSL/HTTPS
4. Set up monitoring and logging
5. Regular backups and disaster recovery

### Phase 4: Enterprise Features
1. Multi-location support
2. Advanced conflict detection
3. Integration with hospital systems
4. Mobile app (iOS/Android)
5. Real-time notifications

---

## Contact & Support

**Questions about endpoints?**
- Check Swagger UI at `/docs` for live documentation
- Review endpoint code in `app/shifts/router.py`

**Database issues?**
- Check PostgreSQL connection string in `.env`
- Run: `python -c "from app.core.db import SessionLocal; db = SessionLocal(); print('Connected!')"`

**Authentication problems?**
- Verify user exists: Check `users` table
- Check password: Use test credentials provided
- Verify token format: Must be `Authorization: Bearer TOKEN`

---

## Summary

This is a fully functional hospital workflow automation system with:
- ✅ Complete REST API
- ✅ Role-based access control
- ✅ Shift management & swaps
- ✅ PostgreSQL database
- ✅ JWT authentication
- ✅ Swagger API documentation
- ✅ Production-ready code

**Ready to deploy and extend!** 🚀





SECRET_KEY=6610dad8b0f0a31ce9cfd49784ecb736e6f3103a16ee1a3bba0140c10170e419
# Local DB Config (Deprecated)
# POSTGRES_HOST=localhost
# POSTGRES_USER=backend_user
# POSTGRES_PASSWORD=strong_backend_password_2024
# POSTGRES_DB=hospital_workflow
# POSTGRES_PORT=5432

# Supabase Configuration (Direct connection, SQLAlchemy URL using psycopg2 driver and SSL)
# From Supabase "Primary Database" → "Direct connection" URI.
DATABASE_URL=postgresql://postgres:vishnudharsh4@db.tmzsabmbdmabjassrzob.supabase.co:5432/postgres



 # from D:\hospital\backend
>> $env:SECRET_KEY = "6610dad8b0f0a31ce9cfd49784ecb736e6f3103a16ee1a3bba0140c10170e419"
>> $env:DATABASE_URL = "postgresql://postgres:vishnudharsh4@db.tmzsabmbdmabjassrzob.supabase.co:5432/postgres"
>> uvicorn app.main:app --reload