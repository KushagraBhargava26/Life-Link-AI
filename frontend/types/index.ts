// frontend/types/index.ts
// LifeLink AI — Global TypeScript Types
// Architecture Reference: ARCHITECTURE.md Section 15 (Frontend Architecture)
// Principle: "Types are shared across the entire frontend from types/index.ts"
//
// Phase 1.1: Type stubs matching API.md response contracts.
// Phase 1.3+: Expand with full type definitions for all API responses.

// =============================================================================
// Standard API Response Envelope
// Architecture Reference: ARCHITECTURE.md Section 23 (Standard API Response Envelope)
// =============================================================================

export interface ApiSuccessResponse<T = unknown> {
  success: true;
  data: T;
  message: string;
  timestamp: number;
  request_id: string;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
  details: Record<string, unknown>;
}

export interface ApiErrorResponse {
  success: false;
  error: ApiErrorDetail;
  timestamp: number;
  request_id: string;
}

export type ApiResponse<T = unknown> = ApiSuccessResponse<T> | ApiErrorResponse;

// =============================================================================
// Pagination
// =============================================================================

export interface PaginationParams {
  page: number;
  page_size: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// =============================================================================
// Blood Type Types
// Architecture Reference: ARCHITECTURE.md ADR-003 (Blood Group Data Model)
// =============================================================================

export type ABOGroup = 'A' | 'B' | 'AB' | 'O';

export interface BloodType {
  abo_group: ABOGroup;
  rh_positive: boolean;
  display: string; // e.g., "O-", "AB+"
}

// =============================================================================
// User and Auth Types
// Architecture Reference: ARCHITECTURE.md Section 18 (Authentication Architecture)
// =============================================================================

export type UserRole =
  | 'SUPER_ADMIN'
  | 'ADMIN'
  | 'HOSPITAL_ADMIN'
  | 'HOSPITAL_STAFF'
  | 'BLOOD_BANK_MANAGER'
  | 'BLOOD_BANK_STAFF'
  | 'DONOR'
  | 'PATIENT'
  | 'GOVERNMENT_ANALYST';

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  phone?: string | null;
  role?: UserRole;
  roles?: string[];
  is_active: boolean;
  is_verified?: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: 'Bearer';
  expires_in: number;
}

// =============================================================================
// Location Types
// Architecture Reference: ARCHITECTURE.md ADR-002 (Donor Location Privacy)
// =============================================================================

export interface Location {
  city: string;
  state: string;
  latitude: number;  // City-centroid latitude (stored permanently)
  longitude: number; // City-centroid longitude (stored permanently)
}

// =============================================================================
// Emergency Types
// Architecture Reference: ARCHITECTURE.md Section 30 (Emergency Workflow)
// =============================================================================

export type EmergencyUrgency = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export type EmergencyStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'AI_MATCHING'
  | 'MATCHING_COMPLETE'
  | 'NO_MATCH_FOUND'
  | 'ALERTS_SENT'
  | 'PENDING_RESPONSE'
  | 'DONOR_CONFIRMED'
  | 'EN_ROUTE'
  | 'BLOOD_RECEIVED'
  | 'CROSS_MATCHED'
  | 'FULFILLED'
  | 'CANCELLED'
  | 'ESCALATED'
  | 'RADIUS_EXPANDED'
  | 'INCOMPATIBLE';

export interface EmergencyRequest {
  id: string;
  blood_type: BloodType;
  units_required: number;
  urgency: EmergencyUrgency;
  status: EmergencyStatus;
  hospital_id: string;
  hospital_name: string;
  created_at: string;
  updated_at: string;
}

export interface EmergencyRequestData {
  id: string;
  request_number: string;
  blood_type: string;
  units_required: number;
  units_fulfilled: number;
  urgency_level: string;
  hospital_name?: string | null;
  facility_address?: string | null;
  city: string;
  status: string;
  ai_assisted: boolean;
  patient_name?: string | null;
  patient_age?: number | null;
  notes?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  created_at: string;
  updated_at: string;
}

export interface CreateEmergencyPayload {
  blood_type: string;
  units_required: number;
  urgency_level: string;
  hospital_name?: string;
  city: string;
  patient_name?: string;
  patient_age?: number;
  notes?: string;
}

// =============================================================================
// Donor Types
// Architecture Reference: ARCHITECTURE.md Section 33 (Donor Workflow)
// =============================================================================

export type DonorAvailabilityStatus = 'AVAILABLE' | 'UNAVAILABLE' | 'COOLING_PERIOD';

export interface Donor {
  id: string;
  user_id: string;
  full_name: string;
  blood_type: BloodType;
  city: string;
  state: string;
  availability_status: DonorAvailabilityStatus;
  last_donation_date: string | null;
  total_donations: number;
}

// =============================================================================
// Notification Types
// Architecture Reference: ARCHITECTURE.md Section 19 (Notification Architecture)
// =============================================================================

export type NotificationType =
  | 'EMERGENCY_ALERT'
  | 'DONOR_MATCH'
  | 'LOW_INVENTORY'
  | 'REQUEST_ACCEPTED'
  | 'DONATION_REMINDER'
  | 'SYSTEM_ALERT';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
}

// =============================================================================
// Hospital Types
// Architecture Reference: ARCHITECTURE.md Section 27; DATABASE.md Section 7
// =============================================================================

export type HospitalType = 'GOVERNMENT' | 'PRIVATE' | 'TRUST' | 'CLINIC' | 'SPECIALTY';

export interface Hospital {
  id: string;
  name: string;
  registration_number?: string | null;
  type: HospitalType;
  address_line: string;
  city: string;
  state: string;
  pincode: string;
  latitude?: number | null;
  longitude?: number | null;
  phone: string;
  email?: string | null;
  website?: string | null;
  bed_count?: number | null;
  has_blood_bank: boolean;
  license_issue_date?: string | null;
  license_expiry_date?: string | null;
  certificate_url?: string | null;
  status?: string;
  is_verified: boolean;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface HospitalCreateData {
  name: string;
  registration_number?: string;
  type: HospitalType;
  address_line: string;
  city: string;
  state: string;
  pincode: string;
  phone: string;
  email?: string;
  website?: string;
  bed_count?: number;
  has_blood_bank?: boolean;
  license_issue_date?: string;
  license_expiry_date?: string;
  certificate_url?: string;
  status?: string;
}

export interface HospitalUpdateData {
  name?: string;
  registration_number?: string;
  type?: HospitalType;
  address_line?: string;
  city?: string;
  state?: string;
  pincode?: string;
  phone?: string;
  email?: string;
  website?: string;
  bed_count?: number;
  has_blood_bank?: boolean;
  license_issue_date?: string;
  license_expiry_date?: string;
  certificate_url?: string;
  status?: string;
}

export interface HospitalDashboardData {
  hospital: Hospital;
  active_requests_count: number;
  pending_requests_count: number;
  recent_requests: Array<{
    id: string;
    request_number: string;
    blood_type: string;
    units_required: number;
    units_fulfilled: number;
    urgency_level: string;
    status: string;
    city: string;
    created_at: string | null;
  }>;
}

// =============================================================================
// Blood Bank Types
// Architecture Reference: ARCHITECTURE.md Section 27; DATABASE.md Section 8
// =============================================================================

export interface BloodBank {
  id: string;
  name: string;
  license_number?: string | null;
  hospital_id?: string | null;
  address_line: string;
  city: string;
  state: string;
  pincode: string;
  latitude?: number | null;
  longitude?: number | null;
  phone: string;
  email?: string | null;
  operating_hours?: string | null;
  is_24_hours: boolean;
  accepts_walk_in: boolean;
  license_issue_date?: string | null;
  license_expiry_date?: string | null;
  certificate_url?: string | null;
  status?: string;
  is_verified: boolean;
  is_active: boolean;
  manager_user_id?: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface BloodBankCreateData {
  name: string;
  license_number?: string;
  hospital_id?: string;
  address_line: string;
  city: string;
  state: string;
  pincode: string;
  phone: string;
  email?: string;
  operating_hours?: string;
  is_24_hours?: boolean;
  accepts_walk_in?: boolean;
  license_issue_date?: string;
  license_expiry_date?: string;
  certificate_url?: string;
  status?: string;
}

export interface BloodBankUpdateData {
  name?: string;
  license_number?: string;
  address_line?: string;
  city?: string;
  state?: string;
  pincode?: string;
  phone?: string;
  email?: string;
  operating_hours?: string;
  is_24_hours?: boolean;
  accepts_walk_in?: boolean;
  license_issue_date?: string;
  license_expiry_date?: string;
  certificate_url?: string;
  status?: string;
}

export interface EmergencyDemandItem {
  id: string;
  request_number: string;
  blood_type: string;
  units_required: number;
  units_fulfilled: number;
  urgency_level: string;
  hospital_name: string;
  city: string;
  status: string;
  created_at: string | null;
}

export interface BloodBankDashboardData {
  blood_bank: BloodBank;
  active_emergency_demand_count: number;
  is_operational: boolean;
  emergency_demand: EmergencyDemandItem[];
}

export interface BloodInventoryItem {
  id: string;
  facility_type: string;
  facility_id: string;
  blood_type: string;
  component: string;
  units_available: number;
  units_reserved: number;
  net_available: number;
  minimum_threshold: number;
  last_restocked_at: string | null;
  expiry_date: string | null;
  is_expired: boolean;
  is_low_stock: boolean;
  created_at: string;
  updated_at: string;
}

export interface InventorySummary {
  total_available: number;
  total_reserved: number;
  expiring_soon_count: number;
  depleted_groups_count: number;
  stock_by_blood_type: Record<string, number>;
}

export interface BloodInventoryUpdatePayload {
  units_available: number;
  minimum_threshold?: number;
  expiry_date?: string | null;
  component?: string;
  reason?: string;
}

export interface CompatibleStockBreakdown {
  blood_type: string;
  units_available: number;
  is_exact_match: boolean;
}

export interface DemandAvailabilityResult {
  request_id: string;
  request_number: string;
  blood_type: string;
  component: string;
  units_required: number;
  urgency_level: string;
  hospital_name: string;
  city: string;
  status: string;
  is_compatible_stock_available: boolean;
  availability_status: 'AVAILABLE' | 'PARTIAL' | 'UNAVAILABLE';
  total_compatible_units: number;
  compatible_breakdown: Array<{
    blood_type: string;
    units_available: number;
    is_exact_match: boolean;
  }>;
}

// =============================================================================
// Matching Engine Types (Phase 1.6)
// Architecture Reference: ARCHITECTURE.md ADR-004 & Section 17
// =============================================================================

export type MatchCandidateType = 'DONOR' | 'BLOOD_BANK';
export type MatchCandidateStatus = 'PROPOSED' | 'SHORTLISTED' | 'DISMISSED';
export type MatchRunStatus = 'INITIATED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'NO_CANDIDATES';

export interface MatchCandidate {
  id: string;
  rank: number;
  candidate_type: MatchCandidateType;
  candidate_id: string;
  name: string;
  blood_type: string;
  compatibility_status?: string;
  total_score: number;
  compatibility_score: number;
  proximity_score: number;
  availability_score: number;
  ai_score?: number | null;
  distance_km?: number | null;
  location_display: string;
  units_available?: number | null;
  status: MatchCandidateStatus;
  donor_response_status?: string | null;
  blood_bank_response_status?: string | null;
  units_committed?: number | null;
  explanation: string[];
}

export interface MatchRun {
  id: string;
  emergency_request_id: string;
  run_number: number;
  status: MatchRunStatus;
  model_version: string;
  algorithm: string;
  search_radius_km: number;
  candidates_evaluated: number;
  donors_matched: number;
  blood_banks_matched: number;
  execution_duration_ms?: number | null;
  created_at: string;
  blood_banks: MatchCandidate[];
  donors: MatchCandidate[];
}

export interface CandidateStatusUpdatePayload {
  status: MatchCandidateStatus;
}

export interface DonorOpportunityResponse {
  id: string;
  emergency_request_id: string;
  donor_id: string;
  status: 'ACCEPTED' | 'DECLINED' | 'PENDING';
  notes?: string | null;
  responded_at: string;
  created_at: string;
}

export interface DonorOpportunityDetail {
  id: string;
  request_number: string;
  blood_type: string;
  component: string;
  units_requested: number;
  units_fulfilled: number;
  urgency_level: string;
  hospital_name?: string | null;
  facility_address?: string | null;
  city: string;
  status: string;
  created_at: string;
  is_compatible: boolean;
  donor_blood_type: string;
  donor_response?: DonorOpportunityResponse | null;
}

export interface DonorOpportunityResponsePayload {
  status: 'ACCEPTED' | 'DECLINED';
  notes?: string;
}

