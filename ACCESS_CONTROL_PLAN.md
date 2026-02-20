# 🏥 Hospital Workflow - Access Control & CRUD Privileges

## 📋 Current Status: READ-ONLY MODE
- ✅ All users can view data (GET endpoints)
- ❌ CRUD operations disabled for now (POST/PUT/DELETE temporarily hidden)

---

## 👥 Role-Based Access Control (RBAC) - READ OPERATIONS

### 1️⃣ **ADMIN** - Full System Access
**Can VIEW:**
- ✅ Users (all staff)
- ✅ Appointments (all)
- ✅ Shifts (all)
- ✅ Rooms (all)
- ✅ Dashboard (system-wide stats)

**Can DO (FUTURE - PHASE 2):**
- Create, Update, Delete users
- Create, Update, Delete shifts
- Create, Update, Delete appointments
- Create, Update, Delete rooms
- Manage system settings

---

### 2️⃣ **HR** - Workforce Management
**Can VIEW:**
- ✅ Users (all staff for assignment)
- ✅ Shifts (all)
- ✅ Appointments (all)
- ✅ Dashboard (staffing stats)

**Can DO (FUTURE - PHASE 2):**
- Create, Update shifts
- Assign staff to shifts
- View shift optimization recommendations
- Cannot: Delete users, override appointments

---

### 3️⃣ **DOCTOR** - Clinical Operations
**Can VIEW:**
- ✅ Appointments (own only)
- ✅ Shifts (own only - via my-shifts)
- ✅ Dashboard (personal stats)

**Can DO (FUTURE - PHASE 2):**
- Update own availability
- Swap assignments with other doctors
- Update appointment status
- Cannot: Create shifts, delete appointments

---

### 4️⃣ **STAFF** - Support Operations
**Can VIEW:**
- ✅ Shifts (own only - via my-shifts)
- ✅ Dashboard (personal schedule)

**Can DO (FUTURE - PHASE 2):**
- Request shift swaps
- View own workload
- Cannot: Create/modify shifts, view appointments

---

## 🔐 Data Visibility Rules (Current)

| Endpoint | Admin | HR | Doctor | Staff |
|----------|-------|----|---------|----|
| GET /users/ | ✅ All | ✅ All | ❌ | ❌ |
| GET /appointments/ | ✅ All | ✅ All | ✅ Own | ❌ |
| GET /shifts/ | ✅ All | ✅ All | ❌ | ❌ |
| GET /shifts/my-shifts | ✅ All | ✅ All | ✅ Own | ✅ Own |
| GET /rooms/ | ✅ All | ✅ All | ❌ | ❌ |

---

## 🚫 Hidden/Disabled Features (PHASE 1)

1. ❌ ML Forecast (`/ml/forecast`) - Not available to any user (training needed)
2. ❌ Shift Optimization (`/ml/shift-optimize`) - Not available
3. ❌ POST Operations (Create) - Temporarily disabled
4. ❌ PUT Operations (Update) - Temporarily disabled
5. ❌ DELETE Operations (Delete) - Temporarily disabled

---

## 📅 Implementation Roadmap

### PHASE 1: READ-ONLY (✅ COMPLETE)
- [x] Users can view their authorized data only
- [x] HR can see user list
- [x] Doctor can see own appointments/shifts
- [x] Staff can see own shifts
- [x] CRUD operations hidden from UI

### PHASE 2: CRUD PRIVILEGES (🚀 NEXT)
- [ ] Admin: Full CRUD on all resources
- [ ] HR: Create/Update shifts, assign staff
- [ ] Doctor: Update availability, swap shifts
- [ ] Staff: Request shift swaps
- [ ] Implement authorization guards for each operation

### PHASE 3: ML MODELS (📊 FUTURE)
- [ ] Train demand forecasting model
- [ ] Train shift optimization model
- [ ] Enable forecasting for Admin/HR only
- [ ] Display recommendations in UI

### PHASE 4: ADVANCED FEATURES (🎯 FUTURE)
- [ ] Audit logging for all CRUD
- [ ] Notification system for changes
- [ ] Approval workflows for critical changes
- [ ] Analytics dashboards

---

## 🔑 Key Implementation Notes

1. **Frontend Filtering**: Only GET endpoints shown in sidebar
2. **Backend Validation**: Each endpoint checks user role on request
3. **Error Responses**: 
   - 403 Forbidden = User role not authorized
   - 404 Not Found = Resource belongs to different user/unauthorized access
4. **Data Filtering**:
   - Admin: No filtering (sees all)
   - HR: No filtering on most resources
   - Doctor: Auto-filters to own records
   - Staff: Auto-filters to own records
