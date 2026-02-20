# Quick Testing Guide - Shift Endpoints

## 🔐 Login Credentials

### For Read My Shifts & Request Swap (Any authenticated user)

**Doctor Accounts:**
| Email | Password | User ID |
|-------|----------|---------|
| doctor1@hospital.com | password123 | 4 |
| doctor2@hospital.com | password123 | 5 |
| doctor3@hospital.com | password123 | 6 |

**Staff Accounts:**
| Email | Password | User ID |
|-------|----------|---------|
| staff1@hospital.com | password123 | 12 |
| staff2@hospital.com | password123 | 13 |
| staff3@hospital.com | password123 | 14 |

**Admin/HR Accounts (for Approve Swap):**
| Email | Password | User ID |
|-------|----------|---------|
| admin@hospital.com | admin123 | 1 |
| hr1@hospital.com | password123 | 2 |

---

## 📋 ENDPOINT 1: Read My Shifts

**Method:** GET  
**URL:** `/api/v1/shifts/my-shifts`  
**Access:** Any authenticated user can see their own shifts

### Step-by-Step Test:

1. **Login** - Use POST `/api/v1/login/access-token`
   - Username: `doctor1@hospital.com`
   - Password: `password123`

2. **Authorize**
   - Copy the `access_token` from response
   - Click "Authorize" button (top right)
   - Enter: `Bearer YOUR_TOKEN_HERE`
   - Click "Authorize" and "Close"

3. **Call Endpoint**
   - Find GET `/api/v1/shifts/my-shifts`
   - Click "Try it out"
   - Click "Execute"
   - **No parameters needed!**

### Expected Response:

```json
[
  {
    "id": 1,
    "staff_id": 4,
    "shift_id": 100,
    "status": "Assigned",
    "target_staff_id": null,
    "created_at": "2026-02-19T11:00:00",
    "updated_at": "2026-02-19T11:00:00"
  },
  {
    "id": 5,
    "staff_id": 4,
    "shift_id": 105,
    "status": "Assigned",
    "target_staff_id": null,
    "created_at": "2026-02-19T12:00:00",
    "updated_at": "2026-02-19T12:00:00"
  }
]
```

### Test Different Users:

**Test as Staff Member:**
1. Logout (click "Authorize" → "Logout")
2. Login as: `staff1@hospital.com` / `password123`
3. Authorize with new token
4. Execute GET `/api/v1/shifts/my-shifts`

**Test as Admin:**
1. Login as: `admin@hospital.com` / `admin123`
2. Authorize with new token
3. Execute GET `/api/v1/shifts/my-shifts`

---

## 🔄 ENDPOINT 2: Request Swap

**Method:** POST  
**URL:** `/api/v1/shifts/swap`  
**Access:** Staff or Doctor (must own the assignment)

### Step-by-Step Test:

1. **Login as Doctor**
   - Username: `doctor1@hospital.com`
   - Password: `password123`

2. **Get Your Assignment IDs**
   - Call GET `/api/v1/shifts/my-shifts`
   - Note down one of your `id` values (e.g., 1, 5, 10)

3. **Request Swap**
   - Find POST `/api/v1/shifts/swap`
   - Click "Try it out"
   - Enter request body:

### Sample Request 1: Doctor to Doctor Swap

```json
{
  "assignment_id": 1,
  "target_staff_id": 5
}
```

**Explanation:**
- `assignment_id`: YOUR shift assignment ID (from my-shifts response)
- `target_staff_id`: Another doctor's user ID (5 = doctor2)

### Sample Request 2: Staff to Staff Swap

**Login as:** `staff1@hospital.com` / `password123`

```json
{
  "assignment_id": 3,
  "target_staff_id": 13
}
```

**Explanation:**
- `assignment_id`: YOUR shift assignment ID
- `target_staff_id`: Another staff member's user ID (13 = staff2)

### Sample Request 3: With Different Target

```json
{
  "assignment_id": 2,
  "target_staff_id": 6
}
```

### Sample Request 4: Multiple Swap Requests

```json
{
  "assignment_id": 7,
  "target_staff_id": 14
}
```

### Sample Request 5: Cross-Department Swap

```json
{
  "assignment_id": 10,
  "target_staff_id": 15
}
```

### Expected Response:

```json
{
  "id": 1,
  "staff_id": 4,
  "shift_id": 100,
  "status": "Assigned",
  "target_staff_id": 5,
  "created_at": "2026-02-19T11:00:00",
  "updated_at": "2026-02-19T14:30:00"
}
```

**Note:** The `target_staff_id` field is now populated with your swap request!

---

## ✅ ENDPOINT 3: Approve Swap

**Method:** POST  
**URL:** `/api/v1/shifts/swap/approve/{assignment_id}`  
**Access:** Admin or HR only

### Step-by-Step Test:

1. **Login as Admin**
   - Username: `admin@hospital.com`
   - Password: `admin123`

2. **Authorize**
   - Copy token
   - Click "Authorize" → Enter: `Bearer YOUR_TOKEN`

3. **Approve Swap**
   - Find POST `/api/v1/shifts/swap/approve/{assignment_id}`
   - Click "Try it out"
   - Enter the assignment ID that has a pending swap
   - Click "Execute"

### Sample Test 1: Approve Assignment 1

**Path Parameter:**
- `assignment_id`: `1`

**No request body needed!**

### Sample Test 2: Approve Assignment 2

**Path Parameter:**
- `assignment_id`: `2`

### Sample Test 3: Approve Assignment 5

**Path Parameter:**
- `assignment_id`: `5`

### Sample Test 4: Approve Assignment 10

**Path Parameter:**
- `assignment_id`: `10`

### Sample Test 5: Test as HR User

**Login as:** `hr1@hospital.com` / `password123`

**Path Parameter:**
- `assignment_id`: `3`

### Expected Response:

```json
{
  "id": 99,
  "staff_id": 5,
  "shift_id": 100,
  "status": "Assigned",
  "target_staff_id": null,
  "created_at": "2026-02-19T15:00:00",
  "updated_at": "2026-02-19T15:00:00"
}
```

**What Happens:**
1. Original assignment (ID 1) is marked as "Swapped"
2. NEW assignment (ID 99) is created for target staff (User ID 5)
3. Response shows the NEW assignment

---

## 🔄 Complete Workflow Example

### Scenario: Doctor 1 wants to swap shift with Doctor 2

**Step 1: Login as Doctor 1**
```
POST /api/v1/login/access-token
username: doctor1@hospital.com
password: password123
```

**Step 2: Check Your Shifts**
```
GET /api/v1/shifts/my-shifts
Authorization: Bearer TOKEN_FROM_STEP1
```

**Response:**
```json
[
  {
    "id": 50,
    "staff_id": 4,
    "shift_id": 110,
    "status": "Assigned",
    ...
  }
]
```

**Step 3: Request Swap**
```
POST /api/v1/shifts/swap
Authorization: Bearer TOKEN_FROM_STEP1

Body:
{
  "assignment_id": 50,
  "target_staff_id": 5
}
```

**Step 4: Login as Admin**
```
POST /api/v1/login/access-token
username: admin@hospital.com
password: admin123
```

**Step 5: Approve Swap**
```
POST /api/v1/shifts/swap/approve/50
Authorization: Bearer TOKEN_FROM_STEP4
```

**Step 6: Verify (Login as Doctor 2)**
```
GET /api/v1/shifts/my-shifts
Authorization: Bearer DOCTOR2_TOKEN
```

**Result:** Doctor 2 now sees the shift!

---

## ❌ Common Errors

### Error 1: 401 Unauthorized
**Reason:** Token expired or not provided  
**Solution:** Re-login and get new token

### Error 2: 403 Forbidden
**Reason:** User doesn't have permission  
**Solution:** 
- For approve swap: Use admin/HR account
- For request swap: Make sure you own the assignment

### Error 3: 404 Not Found
**Reason:** Assignment ID doesn't exist  
**Solution:** Call GET `/api/v1/shifts/my-shifts` to get valid assignment IDs

### Error 4: "Not your shift"
**Reason:** Trying to swap someone else's assignment  
**Solution:** Only swap assignments where `staff_id` matches your user ID

### Error 5: "No target staff specified"
**Reason:** Trying to approve swap that wasn't requested  
**Solution:** First request swap, then approve

---

## 📊 Quick Reference Table

| Endpoint | Method | Who Can Access | Requires Body | Key Field |
|----------|--------|----------------|---------------|-----------|
| /my-shifts | GET | Any user | No | Returns your assignments |
| /swap | POST | Staff/Doctor | Yes | assignment_id + target_staff_id |
| /swap/approve/{id} | POST | Admin/HR | No | Path param: assignment_id |

---

## 🎯 Testing Checklist

**Read My Shifts:**
- [ ] Test as doctor
- [ ] Test as staff
- [ ] Test as admin
- [ ] Verify you only see your own shifts

**Request Swap:**
- [ ] Test doctor to doctor swap
- [ ] Test staff to staff swap
- [ ] Test with valid assignment ID
- [ ] Test with invalid assignment ID (should fail)
- [ ] Test swapping someone else's shift (should fail)

**Approve Swap:**
- [ ] Test as admin
- [ ] Test as HR
- [ ] Test as doctor (should fail - 403)
- [ ] Verify new assignment created
- [ ] Verify original marked as "Swapped"

---

**All endpoints tested and working!** ✅

Server URL: http://127.0.0.1:8000/docs
