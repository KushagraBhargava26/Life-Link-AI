# LifeLink AI — API Contract Document

```
Version      : 3.5
Status       : Implemented & Synchronized through Phase 1.7
Base URL     : /api/v1 (Internal: port 8000 | AI Service: port 8001)
Authors      : LifeLink AI Engineering Team
Last Updated : 2026-09-08
Derived From : ARCHITECTURE.md v3.5, DATABASE.md v3.5
```

> **Authority & Implementation Ground Truth**
> This document defines the exact HTTP API contracts implemented in the FastAPI backend (`backend/app/`) and consumed by the Next.js frontend (`frontend/app/`).
> All endpoints have verified schema validation, ReBAC authorization, and automated test coverage.

---

## Table of Contents

- [1. Global Conventions](#1-global-conventions)
- [2. Authentication and Authorization](#2-authentication-and-authorization)
- [3. Standard Response Envelopes](#3-standard-response-envelopes)
- [4. Error Codes Reference](#4-error-codes-reference)
- [5. Rate Limiting](#5-rate-limiting)
- [6. Auth Endpoints](#6-auth-endpoints)
- [7. Donor Endpoints](#7-donor-endpoints)
- [8. Hospital Endpoints](#8-hospital-endpoints)
- [9. Blood Bank Endpoints](#9-blood-bank-endpoints)
- [10. Inventory Endpoints](#10-inventory-endpoints)
- [11. Emergency Endpoints](#11-emergency-endpoints)
- [12. Matching Engine Endpoints](#12-matching-engine-endpoints)
- [13. Admin Endpoints](#13-admin-endpoints)
- [14. Health Check & Internal AI Endpoints](#14-health-check--internal-ai-endpoints)
- [15. API Endpoint Summary Table](#15-api-endpoint-summary-table)


---

## 1. Global Conventions

### Base URL

```
Development : http://localhost:8000/api/v1
Production  : https://api.lifelink.ai/api/v1
```

### API Versioning
- All endpoints are prefixed with `/api/v1/`.
- When breaking changes are introduced, `/api/v2/` is added alongside v1.
- v1 endpoints are never removed until v2 is fully stable.

### URL Design Rules
- Kebab-case for multi-word resource names: `/emergency-requests`, `/blood-banks`.
- Plural resource names: `/donors`, `/hospitals`, `/notifications`.
- Maximum 2 levels of nesting: `/hospitals/{id}/inventory`.
- Sub-actions via POST subpaths: `/emergency/{id}/accept`.
- Filtering via query parameters: `/donors?blood_type=O-&city=Mumbai`.

### HTTP Methods

| Method | Semantics |
|---|---|
| `GET` | Retrieve a resource or list — never modifies state |
| `POST` | Create a new resource or trigger an action |
| `PUT` | Replace an entire resource |
| `PATCH` | Partially update a resource |
| `DELETE` | Soft-delete a resource |

### Pagination (All List Endpoints)

Every endpoint that returns a list supports pagination via query parameters:

| Parameter | Type | Default | Max | Description |
|---|---|---|---|---|
| `limit` | integer | 20 | 50 | Number of records to return |
| `offset` | integer | 0 | — | Number of records to skip |

Paginated responses always include:
```json
{
  "success": true,
  "data": [],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 0,
    "has_next": true,
    "has_previous": false
  }
}
```

### Date and Time Format
- All timestamps: ISO 8601 UTC — `2026-08-03T11:26:00Z`
- All dates: ISO 8601 — `2026-08-03`

---

## 2. Authentication and Authorization

### Authentication Method
All protected endpoints require a valid JWT access token in the HTTP `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Token Lifecycle

| Token | TTL | How to Obtain |
|---|---|---|
| Access Token | 15 minutes | POST /api/v1/auth/login |
| Refresh Token | 7 days | Stored as HttpOnly cookie automatically |

### Role-Based Authorization

Each endpoint specifies which roles are permitted. Roles are embedded in the JWT payload as the `role` claim.

| Symbol | Meaning |
|---|---|
| `PUBLIC` | No authentication required |
| `ANY_AUTH` | Any authenticated user regardless of role |
| `DONOR` | Users with DONOR role |
| `HOSPITAL_ADMIN` | Users with HOSPITAL_ADMIN role |
| `BLOOD_BANK_MANAGER` | Users with BLOOD_BANK_MANAGER role |
| `PATIENT` | Users with PATIENT role |
| `SUPER_ADMIN` | Users with SUPER_ADMIN role |
| `GOVERNMENT_ANALYST` | Users with GOVERNMENT_ANALYST role |

---

## 3. Standard Response Envelopes

### Success Response

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2026-08-03T11:26:00Z",
  "request_id": "req_abc123"
}
```

### Success Response (List)

```json
{
  "success": true,
  "data": [],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 0,
    "has_next": true,
    "has_previous": false
  },
  "timestamp": "2026-08-03T11:26:00Z",
  "request_id": "req_abc123"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description of what went wrong",
    "details": {}
  },
  "timestamp": "2026-08-03T11:26:00Z",
  "request_id": "req_abc123"
}
```

---

## 4. Error Codes Reference

### HTTP Status Codes Used

| HTTP Code | When Returned |
|---|---|
| `200 OK` | Successful GET, PATCH, PUT, DELETE |
| `201 Created` | Successful POST that creates a new resource |
| `204 No Content` | Successful DELETE with no response body |
| `400 Bad Request` | Malformed request syntax |
| `401 Unauthorized` | Missing, expired, or invalid token |
| `403 Forbidden` | Valid token but insufficient role |
| `404 Not Found` | Resource does not exist |
| `409 Conflict` | Duplicate email, constraint violation |
| `422 Unprocessable Entity` | Pydantic validation failed |
| `429 Too Many Requests` | Rate limit exceeded |
| `503 Service Unavailable` | AI service or external dependency down |
| `500 Internal Server Error` | Unexpected server-side error |

### Application Error Codes

| Error Code | HTTP | Description |
|---|---|---|
| `AUTH_INVALID_CREDENTIALS` | 401 | Wrong email or password |
| `AUTH_TOKEN_EXPIRED` | 401 | Access token has expired |
| `AUTH_TOKEN_INVALID` | 401 | Token signature is invalid or malformed |
| `AUTH_TOKEN_MISSING` | 401 | Authorization header not present |
| `AUTH_INSUFFICIENT_ROLE` | 403 | User does not have required role |
| `AUTH_ACCOUNT_DISABLED` | 403 | User account has been deactivated |
| `USER_EMAIL_ALREADY_EXISTS` | 409 | Registration with existing email |
| `USER_NOT_FOUND` | 404 | User with given ID not found |
| `DONOR_NOT_FOUND` | 404 | Donor profile not found |
| `DONOR_PROFILE_EXISTS` | 409 | User already has a donor profile |
| `DONOR_NOT_ELIGIBLE` | 422 | Donor is within 8-week donation cooldown |
| `HOSPITAL_NOT_FOUND` | 404 | Hospital with given ID not found |
| `HOSPITAL_REGISTRATION_EXISTS` | 409 | Registration number already in use |
| `BLOOD_BANK_NOT_FOUND` | 404 | Blood bank with given ID not found |
| `INVENTORY_NOT_FOUND` | 404 | Inventory record not found |
| `INVENTORY_INSUFFICIENT_STOCK` | 422 | Requested units exceed available stock |
| `EMERGENCY_NOT_FOUND` | 404 | Emergency request not found |
| `EMERGENCY_ALREADY_FULFILLED` | 409 | Request is already in FULFILLED status |
| `EMERGENCY_INVALID_STATUS_TRANSITION` | 422 | Cannot move to requested status from current status |
| `BLOOD_TYPE_INVALID` | 422 | Provided blood type is not a valid ABO+Rh type |
| `AI_SERVICE_UNAVAILABLE` | 503 | AI service unreachable — fallback used |
| `NOTIFICATION_SEND_FAILED` | 500 | Notification delivery failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests from this IP |
| `VALIDATION_ERROR` | 422 | Request body failed schema validation |
| `RESOURCE_NOT_FOUND` | 404 | Generic not found |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 5. Rate Limiting

Rate limiting is enforced at the Nginx and middleware level using Redis counters.

| Category | Limit | Window | Scope |
|---|---|---|---|
| General API requests | 100 requests | 60 seconds | Per IP address |
| Login attempts | 5 requests | 15 minutes | Per IP address |
| Registration | 10 requests | 60 minutes | Per IP address |
| Emergency submission | 10 requests | 60 minutes | Per authenticated user |
| Password reset | 3 requests | 60 minutes | Per IP address |

When limit is exceeded, response is:
```json
HTTP 429 Too Many Requests
Retry-After: 60

{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again in 60 seconds.",
    "details": { "retry_after_seconds": 60 }
  }
}
```

---

## 6. Auth Endpoints

**Module Owner:** Developer 1

---

### POST /api/v1/auth/register

Register a new user account.

**Auth Required:** `PUBLIC`

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass@123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+919876543210",
  "role": "DONOR"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `email` | string | YES | Valid email format, max 255 chars |
| `password` | string | YES | Min 8 chars, 1 uppercase, 1 number, 1 special char |
| `first_name` | string | YES | Max 100 chars |
| `last_name` | string | YES | Max 100 chars |
| `phone` | string | NO | Valid phone format |
| `role` | string | YES | One of: DONOR, PATIENT, HOSPITAL_ADMIN, BLOOD_BANK_MANAGER |

**Success Response — 201:**
```json
{
  "success": true,
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "DONOR",
    "is_verified": false
  },
  "message": "Account created successfully. Please verify your email."
}
```

**Error Responses:**
| Code | Error Code | Scenario |
|---|---|---|
| 409 | `USER_EMAIL_ALREADY_EXISTS` | Email already registered |
| 422 | `VALIDATION_ERROR` | Password too weak, invalid email format |

---

### POST /api/v1/auth/login

Authenticate a user and receive access and refresh tokens.

**Auth Required:** `PUBLIC`

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass@123"
}
```

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "john.doe@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "roles": ["DONOR"],
      "is_verified": true
    }
  },
  "message": "Login successful"
}
```

Note: The refresh token is set as an `HttpOnly` cookie automatically — it does not appear in the response body.

**Error Responses:**
| Code | Error Code | Scenario |
|---|---|---|
| 401 | `AUTH_INVALID_CREDENTIALS` | Wrong email or password |
| 403 | `AUTH_ACCOUNT_DISABLED` | Account deactivated by admin |
| 429 | `RATE_LIMIT_EXCEEDED` | More than 5 failed attempts in 15 minutes |

---

### POST /api/v1/auth/refresh

Obtain a new access token using the refresh token cookie.

**Auth Required:** `PUBLIC` (refresh token in HttpOnly cookie)

**Request Body:** None

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

**Error Responses:**
| Code | Error Code | Scenario |
|---|---|---|
| 401 | `AUTH_TOKEN_EXPIRED` | Refresh token has expired (7 days) |
| 401 | `AUTH_TOKEN_INVALID` | Refresh token is malformed or tampered |

---

### POST /api/v1/auth/logout

Invalidate the current session. Blacklists access token and clears refresh token cookie.

**Auth Required:** `ANY_AUTH`

**Request Body:** None

**Success Response — 200:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### GET /api/v1/auth/me

Returns the authenticated user's profile and roles.

**Auth Required:** `ANY_AUTH`

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+919876543210",
    "roles": ["DONOR"],
    "is_active": true,
    "is_verified": true,
    "last_login_at": "2026-08-03T11:26:00Z",
    "created_at": "2026-07-01T09:00:00Z"
  }
}
```

---

### POST /api/v1/auth/forgot-password

Initiate password reset. Sends a reset email with a one-time token.

**Auth Required:** `PUBLIC`

**Request Body:**
```json
{
  "email": "john.doe@example.com"
}
```

**Success Response — 200:**
```json
{
  "success": true,
  "message": "If this email is registered, a password reset link has been sent."
}
```

Note: The message is intentionally vague to prevent user enumeration.

---

### POST /api/v1/auth/reset-password

Reset password using a valid reset token.

**Auth Required:** `PUBLIC`

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass@456"
}
```

**Success Response — 200:**
```json
{
  "success": true,
  "message": "Password reset successfully. Please log in with your new password."
}
```

**Error Responses:**
| Code | Error Code | Scenario |
|---|---|---|
| 401 | `AUTH_TOKEN_EXPIRED` | Reset token older than 15 minutes |
| 401 | `AUTH_TOKEN_INVALID` | Token already used or invalid |
| 422 | `VALIDATION_ERROR` | New password too weak |

---

## 7. Donor Endpoints

**Module Owner:** Developer 1

---

### POST /api/v1/donors/profile

Create donor profile for the authenticated user.

**Auth Required:** `ANY_AUTH`

**Request Body:**
```json
{
  "blood_type": "O-",
  "date_of_birth": "1998-06-15",
  "gender": "MALE",
  "weight_kg": 72.5,
  "address_line": "123 MG Road",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "notification_email": true,
  "notification_push": true
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `blood_type` | string | YES | One of 8 valid ABO+Rh types |
| `date_of_birth` | date | YES | Must be 18+ years old |
| `gender` | string | NO | MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY |
| `weight_kg` | number | NO | Must be >= 45 kg |
| `city` | string | NO | Max 100 chars |
| `state` | string | NO | Max 100 chars |

**Success Response — 201:**
```json
{
  "success": true,
  "data": {
    "id": "donor-uuid",
    "user_id": "user-uuid",
    "blood_type": "O-",
    "city": "Mumbai",
    "state": "Maharashtra",
    "is_available": true,
    "is_eligible": true,
    "total_donations": 0,
    "created_at": "2026-08-03T11:26:00Z"
  },
  "message": "Donor profile created successfully"
}
```

**Error Responses:**
| Code | Error Code | Scenario |
|---|---|---|
| 409 | `DONOR_PROFILE_EXISTS` | User already has a donor profile |
| 422 | `BLOOD_TYPE_INVALID` | Invalid blood type string |
| 422 | `VALIDATION_ERROR` | Weight below 45kg, age below 18 |

---

### GET /api/v1/donors/profile

Get authenticated donor's own profile.

**Auth Required:** `DONOR`

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "id": "donor-uuid",
    "user_id": "user-uuid",
    "blood_type": "O-",
    "date_of_birth": "1998-06-15",
    "gender": "MALE",
    "weight_kg": 72.5,
    "city": "Mumbai",
    "state": "Maharashtra",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "is_available": true,
    "is_eligible": true,
    "last_donation_date": null,
    "total_donations": 3,
    "notification_email": true,
    "notification_push": true,
    "created_at": "2026-07-01T09:00:00Z",
    "updated_at": "2026-08-01T14:30:00Z"
  }
}
```

---

### PATCH /api/v1/donors/profile

Update authenticated donor's profile fields.

**Auth Required:** `DONOR`

**Request Body (all fields optional — send only what changes):**
```json
{
  "city": "Pune",
  "state": "Maharashtra",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "weight_kg": 75.0,
  "notification_push": false
}
```

**Success Response — 200:**
```json
{
  "success": true,
  "data": { "...updated donor profile..." },
  "message": "Profile updated successfully"
}
```

---

### PATCH /api/v1/donors/availability

Toggle donor availability status.

**Auth Required:** `DONOR`

**Request Body:**
```json
{
  "is_available": false
}
```

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "is_available": false,
    "updated_at": "2026-08-03T11:26:00Z"
  },
  "message": "Availability updated to unavailable"
}
```

---

### GET /api/v1/donors

Search donors by blood type, city, and availability. Used by hospital staff and admins.

**Auth Required:** `HOSPITAL_ADMIN`, `BLOOD_BANK_MANAGER`, `SUPER_ADMIN`

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `blood_type` | string | NO | Filter by ABO+Rh blood type |
| `city` | string | NO | Filter by city |
| `is_available` | boolean | NO | Filter by availability |
| `is_eligible` | boolean | NO | Filter by eligibility |
| `limit` | integer | NO | Default 20, max 50 |
| `offset` | integer | NO | Default 0 |

**Example Request:**
```
GET /api/v1/donors?blood_type=O-&city=Mumbai&is_available=true&limit=10
```

**Success Response — 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "donor-uuid",
      "blood_type": "O-",
      "city": "Mumbai",
      "is_available": true,
      "is_eligible": true,
      "total_donations": 5,
      "last_donation_date": "2026-05-20",
      "distance_km": 2.4
    }
  ],
  "pagination": {
    "total": 47,
    "limit": 10,
    "offset": 0,
    "has_next": true,
    "has_previous": false
  }
}
```

Note: Full personal details (name, phone, email) are not returned in list responses. Contact information is only revealed after a donor accepts an emergency match.

---

### GET /api/v1/donors/{donor_id}

Get a specific donor's public profile.

**Auth Required:** `HOSPITAL_ADMIN`, `BLOOD_BANK_MANAGER`, `SUPER_ADMIN`

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "id": "donor-uuid",
    "blood_type": "O-",
    "city": "Mumbai",
    "state": "Maharashtra",
    "is_available": true,
    "is_eligible": true,
    "total_donations": 5,
    "last_donation_date": "2026-05-20"
  }
}
```

---

### GET /api/v1/donors/history

Get the authenticated donor's donation history.

**Auth Required:** `DONOR`

**Query Parameters:** `limit`, `offset`

**Success Response — 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "history-uuid",
      "donation_date": "2026-05-20",
      "blood_type": "O-",
      "units_donated": 1,
      "facility_name": "Lilavati Hospital Blood Bank",
      "emergency_request_id": "emr-uuid",
      "created_at": "2026-05-20T10:30:00Z"
    }
  ],
  "pagination": { "..." }
}
```

---

### PATCH /api/v1/donors/fcm-token

Update the Firebase Cloud Messaging token for push notifications.

**Auth Required:** `DONOR`

**Request Body:**
```json
{
  "fcm_token": "firebase-device-token-string"
}
```

**Success Response — 200:**
```json
{
  "success": true,
  "message": "Push notification token updated"
}
```

---

### GET /api/v1/donors/me/opportunities/{request_id}

Get detailed clinical requisition summary and donor's compatibility & response status for a specific emergency opportunity.

**Auth Required:** `DONOR`

**Path Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `request_id` | UUID | YES | Emergency Request ID |

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "id": "emr-uuid",
    "request_code": "EMR-2026-0001",
    "hospital_name": "Apollo Emergency Trauma Center",
    "hospital_city": "Mumbai",
    "hospital_state": "Maharashtra",
    "hospital_address": "Plot 12, Health City, Sector 4",
    "blood_type_needed": "O-",
    "units_needed": 2,
    "urgency": "CRITICAL",
    "created_at": "2026-09-08T10:00:00Z",
    "is_compatible": true,
    "donor_blood_type": "O-",
    "donor_response_status": null,
    "donor_response_notes": null,
    "donor_responded_at": null,
    "can_respond": true,
    "cooldown_remaining_days": 0
  }
}
```

**Error Responses:**
| Code | Error Code | Scenario |
|---|---|---|
| 401 | `AUTH_REQUIRED` | Unauthenticated request |
| 404 | `NOT_FOUND` | Emergency request or donor profile not found |

---

### POST /api/v1/donors/me/opportunities/{request_id}/respond

Submit an explicit acceptance (`ACCEPTED`) or decline (`DECLINED`) response to an emergency blood opportunity.

**Auth Required:** `DONOR`

**Path Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `request_id` | UUID | YES | Emergency Request ID |

**Request Body:**
```json
{
  "response": "ACCEPTED",
  "notes": "I can arrive within 30 minutes. Contact me on phone."
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `response` | string | YES | `ACCEPTED` or `DECLINED` |
| `notes` | string | NO | Max 500 characters |

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "id": "response-uuid",
    "emergency_request_id": "emr-uuid",
    "donor_id": "donor-uuid",
    "response_status": "ACCEPTED",
    "notes": "I can arrive within 30 minutes. Contact me on phone.",
    "responded_at": "2026-09-08T10:15:00Z"
  },
  "message": "Response recorded successfully"
}
```

**Error Responses:**
| Code | Error Code | Scenario |
|---|---|---|
| 401 | `AUTH_REQUIRED` | Unauthenticated request |
| 404 | `NOT_FOUND` | Emergency request or donor profile not found |
| 422 | `VALIDATION_ERROR` | Request inactive, donor within 56-day cooldown, or blood incompatible |

---

## 8. Hospital Endpoints

**Module Owner:** Developer 2

---

### POST /api/v1/hospitals

Register a new hospital.

**Auth Required:** `HOSPITAL_ADMIN`, `SUPER_ADMIN`

**Request Body:**
```json
{
  "name": "Lilavati Hospital",
  "registration_number": "MH-HOSP-001",
  "type": "PRIVATE",
  "address_line": "A-791, Bandra Reclamation",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400050",
  "latitude": 19.0607,
  "longitude": 72.8362,
  "phone": "+912226560000",
  "email": "admin@lilavati.org",
  "website": "https://lilavati.org",
  "bed_count": 323,
  "has_blood_bank": true
}
```

**Success Response — 201:**
```json
{
  "success": true,
  "data": {
    "id": "hospital-uuid",
    "name": "Lilavati Hospital",
    "type": "PRIVATE",
    "city": "Mumbai",
    "is_verified": false,
    "is_active": true,
    "created_at": "2026-08-03T11:26:00Z"
  },
  "message": "Hospital registered. Pending admin verification."
}
```

---

### GET /api/v1/hospitals

List all registered hospitals. Filterable.

**Auth Required:** `ANY_AUTH`

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `city` | string | Filter by city |
| `state` | string | Filter by state |
| `type` | string | Filter by hospital type |
| `is_verified` | boolean | Filter by verification status |
| `has_blood_bank` | boolean | Filter hospitals with blood banks |
| `limit` | integer | Default 20, max 50 |
| `offset` | integer | Default 0 |

**Success Response — 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "hospital-uuid",
      "name": "Lilavati Hospital",
      "type": "PRIVATE",
      "city": "Mumbai",
      "state": "Maharashtra",
      "phone": "+912226560000",
      "has_blood_bank": true,
      "is_verified": true,
      "latitude": 19.0607,
      "longitude": 72.8362
    }
  ],
  "pagination": { "..." }
}
```

---

### GET /api/v1/hospitals/{hospital_id}

Get detailed profile of a specific hospital.

**Auth Required:** `ANY_AUTH`

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "id": "hospital-uuid",
    "name": "Lilavati Hospital",
    "registration_number": "MH-HOSP-001",
    "type": "PRIVATE",
    "address_line": "A-791, Bandra Reclamation",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400050",
    "phone": "+912226560000",
    "email": "admin@lilavati.org",
    "website": "https://lilavati.org",
    "bed_count": 323,
    "has_blood_bank": true,
    "is_verified": true,
    "is_active": true,
    "created_at": "2026-07-01T09:00:00Z"
  }
}
```

---

### PATCH /api/v1/hospitals/{hospital_id}

Update hospital profile fields.

**Auth Required:** `HOSPITAL_ADMIN` (own hospital only), `SUPER_ADMIN`

**Request Body (partial update — send only changed fields):**
```json
{
  "phone": "+912226560001",
  "bed_count": 350
}
```

**Success Response — 200:**
```json
{
  "success": true,
  "data": { "...updated hospital profile..." },
  "message": "Hospital profile updated"
}
```

---

### GET /api/v1/hospitals/{hospital_id}/inventory

Get blood inventory for a specific hospital.

**Auth Required:** `ANY_AUTH`

**Success Response — 200:**
```json
{
  "success": true,
  "data": [
    {
      "blood_type": "O-",
      "units_available": 15,
      "units_reserved": 2,
      "minimum_threshold": 5,
      "last_restocked_at": "2026-08-02T08:00:00Z",
      "expiry_date": "2026-08-30"
    },
    {
      "blood_type": "O+",
      "units_available": 8,
      "units_reserved": 0,
      "minimum_threshold": 10,
      "last_restocked_at": "2026-07-28T14:00:00Z",
      "expiry_date": "2026-08-25"
    }
  ]
}
```

---

### POST /api/v1/hospitals/{hospital_id}/staff

Add a staff member to a hospital.

**Auth Required:** `HOSPITAL_ADMIN` (own hospital), `SUPER_ADMIN`

**Request Body:**
```json
{
  "user_id": "user-uuid",
  "designation": "Blood Bank Officer",
  "can_manage_inventory": true,
  "can_create_requests": true
}
```

**Success Response — 201:**
```json
{
  "success": true,
  "data": {
    "id": "staff-uuid",
    "user_id": "user-uuid",
    "hospital_id": "hospital-uuid",
    "designation": "Blood Bank Officer",
    "can_manage_inventory": true
  },
  "message": "Staff member added to hospital"
}
```

---

## 9. Blood Bank Endpoints

**Module Owner:** Developer 2

---

### POST /api/v1/blood-banks

Register a new blood bank.

**Auth Required:** `BLOOD_BANK_MANAGER`, `SUPER_ADMIN`

**Request Body:**
```json
{
  "name": "Rotary Blood Bank",
  "license_number": "MH-BB-2026-001",
  "hospital_id": null,
  "address_line": "10 Linking Road",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400054",
  "latitude": 19.0832,
  "longitude": 72.8295,
  "phone": "+912226440000",
  "email": "info@rotarybb.org",
  "operating_hours": "8:00 AM – 8:00 PM",
  "is_24_hours": false,
  "accepts_walk_in": true
}
```

**Success Response — 201:**
```json
{
  "success": true,
  "data": {
    "id": "blood-bank-uuid",
    "name": "Rotary Blood Bank",
    "city": "Mumbai",
    "is_verified": false,
    "is_24_hours": false,
    "created_at": "2026-08-03T11:26:00Z"
  },
  "message": "Blood bank registered. Pending admin verification."
}
```

---

### GET /api/v1/blood-banks

List all blood banks. Filterable.

**Auth Required:** `ANY_AUTH`

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `city` | string | Filter by city |
| `blood_type` | string | Filter banks that have this blood type in stock |
| `is_24_hours` | boolean | Filter 24-hour banks only |
| `is_verified` | boolean | Filter verified banks |
| `latitude` | number | Search center latitude (for distance sorting) |
| `longitude` | number | Search center longitude (for distance sorting) |
| `radius_km` | number | Search radius in km (default 50) |

**Success Response — 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "blood-bank-uuid",
      "name": "Rotary Blood Bank",
      "city": "Mumbai",
      "phone": "+912226440000",
      "is_24_hours": false,
      "is_verified": true,
      "distance_km": 3.2,
      "latitude": 19.0832,
      "longitude": 72.8295
    }
  ],
  "pagination": { "..." }
}
```

---

### GET /api/v1/blood-banks/{blood_bank_id}

Get detailed profile of a specific blood bank.

**Auth Required:** `ANY_AUTH`

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "id": "blood-bank-uuid",
    "name": "Rotary Blood Bank",
    "license_number": "MH-BB-2026-001",
    "hospital_id": null,
    "address_line": "10 Linking Road",
    "city": "Mumbai",
    "state": "Maharashtra",
    "phone": "+912226440000",
    "operating_hours": "8:00 AM – 8:00 PM",
    "is_24_hours": false,
    "accepts_walk_in": true,
    "is_verified": true,
    "latitude": 19.0832,
    "longitude": 72.8295
  }
}
```

---

### GET /api/v1/blood-banks/{blood_bank_id}/inventory

Get blood inventory for a specific blood bank.

**Auth Required:** `ANY_AUTH`

**Success Response — 200** (same structure as hospital inventory endpoint)

---

## 10. Inventory Endpoints

**Module Owner:** Developer 2

---

### PUT /api/v1/inventory/{facility_type}/{facility_id}/{blood_type}

Set or update blood stock for a specific blood type at a facility. Creates the record if it does not exist.

**Auth Required:** `HOSPITAL_ADMIN` (for hospital), `BLOOD_BANK_MANAGER` (for blood bank)

**Path Parameters:**
- `facility_type`: `hospital` or `blood-bank`
- `facility_id`: UUID of the hospital or blood bank
- `blood_type`: One of 8 valid blood types (e.g., `O-`, `AB+`)

**Request Body:**
```json
{
  "units_available": 15,
  "minimum_threshold": 5,
  "expiry_date": "2026-08-30",
  "reason": "Monthly restock from Red Cross donation drive"
}
```

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "facility_type": "BLOOD_BANK",
    "facility_id": "blood-bank-uuid",
    "blood_type": "O-",
    "units_available": 15,
    "units_reserved": 0,
    "minimum_threshold": 5,
    "last_restocked_at": "2026-08-03T11:26:00Z",
    "expiry_date": "2026-08-30"
  },
  "message": "Inventory updated"
}
```

---

### PATCH /api/v1/inventory/{facility_type}/{facility_id}/{blood_type}/reserve

Reserve units for a pending emergency request. Called internally by the Emergency module.

**Auth Required:** `HOSPITAL_ADMIN`, `BLOOD_BANK_MANAGER`, `SUPER_ADMIN`

**Request Body:**
```json
{
  "units_to_reserve": 2,
  "emergency_request_id": "emr-uuid"
}
```

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "units_available": 15,
    "units_reserved": 2
  },
  "message": "2 units reserved for emergency request EMR-2026-001"
}
```

**Error Responses:**
| Code | Error Code | Scenario |
|---|---|---|
| 422 | `INVENTORY_INSUFFICIENT_STOCK` | Not enough units to reserve |

---

### GET /api/v1/inventory/search

Search for blood inventory availability across all facilities.

**Auth Required:** `ANY_AUTH`

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `blood_type` | string | YES | Blood type to search |
| `city` | string | NO | Limit search to city |
| `min_units` | integer | NO | Minimum units required (default 1) |
| `latitude` | number | NO | Center point for distance sorting |
| `longitude` | number | NO | Center point for distance sorting |

**Success Response — 200:**
```json
{
  "success": true,
  "data": [
    {
      "facility_type": "BLOOD_BANK",
      "facility_id": "blood-bank-uuid",
      "facility_name": "Rotary Blood Bank",
      "city": "Mumbai",
      "blood_type": "O-",
      "units_available": 15,
      "units_reserved": 2,
      "distance_km": 3.2,
      "phone": "+912226440000",
      "is_24_hours": false,
      "latitude": 19.0832,
      "longitude": 72.8295
    }
  ],
  "pagination": { "..." }
}
```

---

### GET /api/v1/inventory/alerts

Get all facilities currently below their minimum stock threshold.

**Auth Required:** `HOSPITAL_ADMIN`, `BLOOD_BANK_MANAGER`, `SUPER_ADMIN`

**Success Response — 200:**
```json
{
  "success": true,
  "data": [
    {
      "facility_type": "HOSPITAL",
      "facility_id": "hospital-uuid",
      "facility_name": "Lilavati Hospital",
      "blood_type": "O+",
      "units_available": 3,
      "minimum_threshold": 10,
      "deficit": 7,
      "city": "Mumbai"
    }
  ]
}
```

---

## 11. Emergency Endpoints

**Module Owner:** Developer 1

---

### POST /api/v1/emergency/requests

Submit a new emergency blood request. Triggers AI matching immediately.

**Auth Required:** `ANY_AUTH`

**Request Body:**
```json
{
  "blood_type": "O-",
  "units_required": 2,
  "urgency_level": "CRITICAL",
  "hospital_id": "hospital-uuid",
  "patient_name": "Ramesh Kumar",
  "patient_age": 45,
  "city": "Mumbai",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "notes": "Post-operative patient. ICU. Cannot accept substitutes."
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `blood_type` | string | YES | Valid ABO+Rh type |
| `units_required` | integer | YES | Between 1 and 20 |
| `urgency_level` | string | YES | CRITICAL, HIGH, MEDIUM, LOW |
| `hospital_id` | UUID | NO | If hospital is registered on platform |
| `patient_name` | string | NO | Optional patient name |
| `patient_age` | integer | NO | Between 1 and 120 |
| `city` | string | NO | City of emergency |
| `latitude` | number | NO | Precise location for proximity matching |
| `longitude` | number | NO | Precise location for proximity matching |
| `notes` | string | NO | Clinical context, max 1000 chars |

**Success Response — 201:**
```json
{
  "success": true,
  "data": {
    "id": "emr-uuid",
    "request_number": "EMR-2026-001",
    "blood_type": "O-",
    "units_required": 2,
    "urgency_level": "CRITICAL",
    "status": "NOTIFIED",
    "ai_assisted": true,
    "matches_found": 5,
    "city": "Mumbai",
    "created_at": "2026-08-03T11:26:00Z"
  },
  "message": "Emergency request created. 5 compatible donors have been notified."
}
```

**Error Responses:**
| Code | Error Code | Scenario |
|---|---|---|
| 422 | `BLOOD_TYPE_INVALID` | Invalid blood type |
| 503 | `AI_SERVICE_UNAVAILABLE` | AI service down — rule-based fallback used (still succeeds) |

---

### GET /api/v1/emergency/requests

Get emergency requests. Filtered by the authenticated user's role.

**Auth Required:** `ANY_AUTH`

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `status` | string | Filter by request status |
| `blood_type` | string | Filter by blood type |
| `urgency_level` | string | Filter by urgency |
| `city` | string | Filter by city |
| `limit` | integer | Default 20 |
| `offset` | integer | Default 0 |

**Access Control:**
- `PATIENT` / `DONOR`: Can only see their own requests.
- `HOSPITAL_ADMIN`: Can see requests for their hospital.
- `SUPER_ADMIN` / `GOVERNMENT_ANALYST`: Can see all requests.

**Success Response — 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "emr-uuid",
      "request_number": "EMR-2026-001",
      "blood_type": "O-",
      "units_required": 2,
      "units_fulfilled": 0,
      "urgency_level": "CRITICAL",
      "status": "NOTIFIED",
      "city": "Mumbai",
      "created_at": "2026-08-03T11:26:00Z"
    }
  ],
  "pagination": { "..." }
}
```

---

### GET /api/v1/emergency/requests/{request_id}

Get detailed information for a specific emergency request.

**Auth Required:** `ANY_AUTH` (access enforced by ownership)

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "id": "emr-uuid",
    "request_number": "EMR-2026-001",
    "blood_type": "O-",
    "units_required": 2,
    "units_fulfilled": 0,
    "urgency_level": "CRITICAL",
    "status": "NOTIFIED",
    "ai_assisted": true,
    "hospital": {
      "id": "hospital-uuid",
      "name": "Lilavati Hospital",
      "city": "Mumbai",
      "phone": "+912226560000"
    },
    "matches": [
      {
        "rank": 1,
        "match_type": "DONOR",
        "blood_type": "O-",
        "distance_km": 2.4,
        "compatibility_score": 0.98,
        "response": "ACCEPTED"
      },
      {
        "rank": 2,
        "match_type": "BLOOD_BANK",
        "facility_name": "Rotary Blood Bank",
        "distance_km": 3.2,
        "units_available": 15,
        "response": null
      }
    ],
    "notes": "Post-operative patient. ICU.",
    "created_at": "2026-08-03T11:26:00Z",
    "updated_at": "2026-08-03T11:30:00Z"
  }
}
```

---

### POST /api/v1/emergency/requests/{request_id}/cancel

Cancel an emergency request.

**Auth Required:** Creator of the request, or `SUPER_ADMIN`

**Request Body:**
```json
{
  "reason": "Blood was found through another source"
}
```

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "id": "emr-uuid",
    "status": "CANCELLED",
    "cancelled_at": "2026-08-03T12:00:00Z"
  },
  "message": "Emergency request cancelled"
}
```

---

### POST /api/v1/emergency/matches/{match_id}/respond

Donor responds to an emergency match notification.

**Auth Required:** `DONOR` (must be the matched donor)

**Request Body:**
```json
{
  "response": "ACCEPTED",
  "notes": "I can reach the hospital within 30 minutes"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `response` | string | YES | ACCEPTED or DECLINED |
| `notes` | string | NO | Optional message, max 500 chars |

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "match_id": "match-uuid",
    "response": "ACCEPTED",
    "emergency_request": {
      "request_number": "EMR-2026-001",
      "blood_type": "O-",
      "hospital_name": "Lilavati Hospital",
      "hospital_phone": "+912226560000",
      "city": "Mumbai"
    }
  },
  "message": "Response recorded. The requester has been notified."
}
```

## 12. Matching Engine Endpoints

---

### POST /api/v1/emergency/requests/{request_id}/match

Executes multi-tier candidate discovery (blood banks and donors) and triggers advisory AI ranking.

**Auth Required:** `HOSPITAL_ADMIN`, `HOSPITAL_STAFF`, `SUPER_ADMIN`  
*(Caller must be affiliated with the requesting hospital or be a system administrator).*

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `search_radius_km` | float | 50.0 | Radius in km: `15.0` (Local), `25.0` (District), `50.0` (Regional), `100.0` (Intercity) |

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "match_run_id": "8f3b2e1a-4c5d-6e7f-8a9b-0c1d2e3f4a5b",
    "emergency_request_id": "3c2a1b0f-9e8d-7c6b-5a4f-3e2d1c0b9a8f",
    "search_radius_km": 50.0,
    "total_candidates_found": 8,
    "blood_banks_found": 3,
    "donors_found": 5,
    "execution_duration_ms": 42.5,
    "algorithm_version": "hybrid-rule-ai-v1",
    "status": "SUCCESS",
    "candidates": [
      {
        "id": "cand-uuid-1",
        "candidate_type": "BLOOD_BANK",
        "facility_id": "bb-uuid-1",
        "name": "Central Red Cross Blood Bank",
        "city": "Mumbai",
        "distance_km": 4.2,
        "available_units": 12,
        "compatibility_score": 1.0,
        "proximity_score": 0.916,
        "availability_score": 1.0,
        "total_score": 0.979,
        "rank": 1,
        "status": "RECOMMENDED",
        "explanation": [
          "Exact ABO/Rh match (O-)",
          "12 units available in stock",
          "4.2 km from emergency facility"
        ]
      },
      {
        "id": "cand-uuid-2",
        "candidate_type": "DONOR",
        "donor_id": "donor-uuid-1",
        "masked_name": "Donor #A1B2",
        "city": "Mumbai",
        "distance_km": 6.8,
        "compatibility_score": 1.0,
        "proximity_score": 0.864,
        "availability_score": 1.0,
        "response_propensity_score": 0.785,
        "total_score": 0.937,
        "rank": 2,
        "status": "RECOMMENDED",
        "explanation": [
          "Exact ABO/Rh match (O-)",
          "Active and clinically eligible (cooldown passed)",
          "High historical response propensity (78%)",
          "6.8 km from emergency facility"
        ]
      }
    ]
  },
  "message": "Candidate matching completed successfully"
}
```

---

### GET /api/v1/emergency/requests/{request_id}/matches

Retrieves the latest ranked candidate list for an emergency requisition.

**Auth Required:** `HOSPITAL_ADMIN`, `HOSPITAL_STAFF`, `SUPER_ADMIN`

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "match_run_id": "8f3b2e1a-4c5d-6e7f-8a9b-0c1d2e3f4a5b",
    "emergency_request_id": "3c2a1b0f-9e8d-7c6b-5a4f-3e2d1c0b9a8f",
    "search_radius_km": 50.0,
    "candidates": [ "..." ]
  }
}
```

---

### PATCH /api/v1/emergency/requests/{request_id}/matches/{candidate_id}

Updates the coordination status of a specific candidate (e.g. `NOTIFIED`, `ACCEPTED`, `ALLOCATED`, `REJECTED`).

**Auth Required:** `HOSPITAL_ADMIN`, `HOSPITAL_STAFF`, `SUPER_ADMIN`

**Request Body:**
```json
{
  "status": "NOTIFIED",
  "notes": "Coordinating via facility phone"
}
```

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "candidate_id": "cand-uuid-1",
    "status": "NOTIFIED"
  },
  "message": "Candidate status updated"
}
```

---

## 13. Admin Endpoints

---

### GET /api/v1/admin/verifications/pending

Retrieves all hospital and blood bank accounts awaiting institutional verification.

**Auth Required:** `SUPER_ADMIN`, `SYSTEM_ADMIN`

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "pending_hospitals": [
      {
        "id": "hosp-uuid",
        "name": "Apex City Hospital",
        "license_number": "MAH-HOSP-2026-99",
        "city": "Pune",
        "state": "Maharashtra",
        "contact_phone": "+919876543210",
        "contact_email": "admin@apexcity.org",
        "is_verified": false,
        "created_at": "2026-09-08T08:00:00Z"
      }
    ],
    "pending_blood_banks": [
      {
        "id": "bb-uuid",
        "name": "Apex Blood Center",
        "license_number": "BB-LIC-8841",
        "city": "Pune",
        "state": "Maharashtra",
        "contact_phone": "+919876543211",
        "is_verified": false,
        "created_at": "2026-09-08T08:15:00Z"
      }
    ]
  },
  "message": "Pending verifications retrieved"
}
```

---

### PATCH /api/v1/admin/hospitals/{hospital_id}/verify

Approves institutional verification for a registered hospital facility.

**Auth Required:** `SUPER_ADMIN`, `SYSTEM_ADMIN`

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "hospital_id": "hosp-uuid",
    "is_verified": true
  },
  "message": "Hospital verified successfully"
}
```

---

### PATCH /api/v1/admin/blood-banks/{blood_bank_id}/verify

Approves institutional verification for a registered blood bank facility.

**Auth Required:** `SUPER_ADMIN`, `SYSTEM_ADMIN`

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "blood_bank_id": "bb-uuid",
    "is_verified": true
  },
  "message": "Blood bank verified successfully"
}
```

---

## 14. Health Check & Internal AI Endpoints

---

### GET /health

System health check. Returns status of backend service.

**Auth Required:** `PUBLIC`

**Success Response — 200:**
```json
{
  "success": true,
  "data": {
    "service": "backend",
    "status": "healthy",
    "app_name": "LifeLink AI",
    "version": "1.0.0",
    "environment": "development",
    "timestamp": 1725796800.0
  },
  "message": "LifeLink AI backend is running"
}
```

---

### POST /matching/rank (Internal AI Microservice — Port 8001)

Internal microservice endpoint called exclusively by `AiGatewayService` to predict donor response propensity.

**Auth Required:** Internal Docker network isolation

**Request Body:**
```json
{
  "candidates": [
    {
      "donor_id": "donor-uuid-1",
      "recency_months": 3.5,
      "frequency_donations": 6,
      "time_months": 24.0,
      "distance_km": 6.8,
      "compatibility_score": 1.0,
      "availability_score": 1.0
    }
  ],
  "search_radius_km": 50.0
}
```

**Success Response — 200:**
```json
{
  "model_version": "donor-response-v1",
  "ranked_candidates": [
    {
      "donor_id": "donor-uuid-1",
      "response_propensity": 0.785,
      "ai_score": 0.937,
      "rank": 1
    }
  ]
}
```

---

## 15. API Endpoint Summary Table

The following 32 endpoints are fully implemented, authenticated, tested, and mounted in `backend/app/main.py`:

| # | Method | Endpoint Path | Tag / Module | Required Authorization |
|:---:|:---:|---|---|---|
| 1 | `POST` | `/api/v1/auth/register` | Authentication | `PUBLIC` |
| 2 | `POST` | `/api/v1/auth/login` | Authentication | `PUBLIC` |
| 3 | `POST` | `/api/v1/auth/refresh` | Authentication | `PUBLIC` (Refresh Token) |
| 4 | `POST` | `/api/v1/auth/logout` | Authentication | Authenticated User |
| 5 | `GET` | `/api/v1/auth/me` | Authentication | Authenticated User |
| 6 | `PATCH` | `/api/v1/auth/me` | Authentication | Authenticated User |
| 7 | `POST` | `/api/v1/donors/register` | Donors | Authenticated User |
| 8 | `GET` | `/api/v1/donors/me` | Donors | Authenticated Donor |
| 9 | `PUT` | `/api/v1/donors/me` | Donors | Authenticated Donor |
| 10 | `GET` | `/api/v1/donors/me/dashboard` | Donors | Authenticated Donor |
| 11 | `POST` | `/api/v1/donors/me/availability` | Donors | Authenticated Donor |
| 12 | `POST` | `/api/v1/hospitals/register` | Hospitals | Authenticated User / Admin |
| 13 | `GET` | `/api/v1/hospitals/me` | Hospitals | `HOSPITAL_ADMIN`, `HOSPITAL_STAFF` |
| 14 | `GET` | `/api/v1/hospitals/{hospital_id}` | Hospitals | Authenticated User |
| 15 | `GET` | `/api/v1/hospitals/me/dashboard` | Hospitals | `HOSPITAL_ADMIN`, `HOSPITAL_STAFF` |
| 16 | `GET` | `/api/v1/hospitals/me/requests` | Hospitals | `HOSPITAL_ADMIN`, `HOSPITAL_STAFF` |
| 17 | `POST` | `/api/v1/blood-banks/register` | Blood Banks | Authenticated User / Admin |
| 18 | `GET` | `/api/v1/blood-banks/me` | Blood Banks | `BLOOD_BANK_MANAGER`, `BLOOD_BANK_STAFF` |
| 19 | `GET` | `/api/v1/blood-banks/{blood_bank_id}` | Blood Banks | Authenticated User |
| 20 | `GET` | `/api/v1/blood-banks/me/dashboard` | Blood Banks | `BLOOD_BANK_MANAGER`, `BLOOD_BANK_STAFF` |
| 21 | `GET` | `/api/v1/blood-banks/me/demand` | Blood Banks | `BLOOD_BANK_MANAGER`, `BLOOD_BANK_STAFF` |
| 22 | `GET` | `/api/v1/inventory/my` | Blood Bank Inventory | `BLOOD_BANK_MANAGER`, `BLOOD_BANK_STAFF` |
| 23 | `POST` | `/api/v1/inventory/add` | Blood Bank Inventory | `BLOOD_BANK_MANAGER`, `BLOOD_BANK_STAFF` |
| 24 | `PUT` | `/api/v1/inventory/{inventory_id}` | Inventory | `BLOOD_BANK_MANAGER`, `BLOOD_BANK_STAFF` |
| 25 | `DELETE` | `/api/v1/inventory/{inventory_id}` | Inventory | `BLOOD_BANK_MANAGER`, `BLOOD_BANK_STAFF` |
| 26 | `GET` | `/api/v1/inventory/availability` | Inventory | Authenticated User |
| 27 | `GET` | `/api/v1/inventory/history/{inventory_id}` | Inventory | `BLOOD_BANK_MANAGER`, `BLOOD_BANK_STAFF` |
| 28 | `POST` | `/api/v1/emergency/requests` | Emergency Requisitions | `PUBLIC` / Authenticated User |
| 29 | `GET` | `/api/v1/emergency/requests/{request_id}` | Emergency Requisitions | Requester / Hospital / Admin |
| 30 | `GET` | `/api/v1/emergency/track/{request_code}` | Public Tracking | `PUBLIC` (Zero-PII Payload) |
| 31 | `PATCH` | `/api/v1/emergency/requests/{request_id}/status` | Emergency Requisitions | Requisition Hospital / Admin |
| 32 | `POST` | `/api/v1/emergency/requests/{request_id}/match` | Matching & Coordination | Request Hospital Staff / Admin |
| 33 | `GET` | `/api/v1/emergency/requests/{request_id}/matches` | Matching & Coordination | Request Hospital Staff / Admin |
| 34 | `PATCH` | `/api/v1/emergency/requests/{request_id}/matches/{cand_id}` | Matching & Coordination | Request Hospital Staff / Admin |
| 35 | `GET` | `/api/v1/admin/verifications/pending` | System Admin | `SUPER_ADMIN`, `SYSTEM_ADMIN` |
| 36 | `PATCH` | `/api/v1/admin/hospitals/{hospital_id}/verify` | System Admin | `SUPER_ADMIN`, `SYSTEM_ADMIN` |
| 37 | `PATCH` | `/api/v1/admin/blood-banks/{blood_bank_id}/verify` | System Admin | `SUPER_ADMIN`, `SYSTEM_ADMIN` |
| 38 | `GET` | `/health` | Health & Status | `PUBLIC` |

---

*LifeLink AI — API Contract Document*  
*Version 3.5 — Synchronized through Phase 1.7*  
*Derived from ARCHITECTURE.md v3.5 and DATABASE.md v3.5*

