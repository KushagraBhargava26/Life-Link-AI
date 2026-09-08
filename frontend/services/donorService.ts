// frontend/services/donorService.ts
// LifeLink AI — Donor Service Layer
// Architecture Reference: ARCHITECTURE.md Section 15 & Section 33

import { api } from '@/lib/api';
import { ApiSuccessResponse } from '@/types';

export interface DonorProfileData {
  id: string;
  user_id: string;
  blood_type: string;
  city: string;
  state?: string | null;
  pincode?: string | null;
  weight_kg?: number | null;
  date_of_birth?: string | null;
  gender?: string | null;
  address_line?: string | null;
  is_available: boolean;
  is_eligible: boolean;
  last_donation_date?: string | null;
  total_donations: number;
  created_at: string;
  updated_at: string;
}

export interface SaveDonorPayload {
  blood_type: string;
  city: string;
  state?: string;
  pincode?: string;
  weight_kg?: number;
  date_of_birth?: string;
  gender?: string;
  address_line?: string;
  is_available?: boolean;
}

export interface CompatibleEmergencyOpportunity {
  id: string;
  request_number: string;
  blood_type: string;
  component: string;
  units_requested: number;
  urgency_level: string;
  hospital_name?: string | null;
  city: string;
  state: string;
  created_at: string;
}

export interface DonorDashboardData {
  profile?: DonorProfileData | null;
  has_profile: boolean;
  is_available: boolean;
  is_eligible: boolean;
  next_eligible_date?: string | null;
  days_until_eligible: number;
  total_donations: number;
  estimated_lives_saved: number;
  compatible_opportunities: CompatibleEmergencyOpportunity[];
}

export const donorService = {
  async getProfile(): Promise<ApiSuccessResponse<DonorProfileData>> {
    const response = await api.get<ApiSuccessResponse<DonorProfileData>>('/donors/me');
    return response.data;
  },

  async getDashboard(): Promise<ApiSuccessResponse<DonorDashboardData>> {
    const response = await api.get<ApiSuccessResponse<DonorDashboardData>>('/donors/me/dashboard');
    return response.data;
  },

  async saveProfile(payload: SaveDonorPayload): Promise<ApiSuccessResponse<DonorProfileData>> {
    const response = await api.post<ApiSuccessResponse<DonorProfileData>>('/donors', payload);
    return response.data;
  },

  async updateProfile(payload: Partial<SaveDonorPayload>): Promise<ApiSuccessResponse<DonorProfileData>> {
    const response = await api.put<ApiSuccessResponse<DonorProfileData>>('/donors/me', payload);
    return response.data;
  },

  async toggleAvailability(is_available: boolean): Promise<ApiSuccessResponse<DonorProfileData>> {
    const response = await api.patch<ApiSuccessResponse<DonorProfileData>>('/donors/me/availability', {
      is_available,
    });
    return response.data;
  },

  async getOpportunity(requestId: string): Promise<ApiSuccessResponse<import('@/types').DonorOpportunityDetail>> {
    const response = await api.get<ApiSuccessResponse<import('@/types').DonorOpportunityDetail>>(
      `/donors/me/opportunities/${requestId}`
    );
    return response.data;
  },

  async respondToOpportunity(
    requestId: string,
    payload: import('@/types').DonorOpportunityResponsePayload
  ): Promise<ApiSuccessResponse<import('@/types').DonorOpportunityResponse>> {
    const response = await api.post<ApiSuccessResponse<import('@/types').DonorOpportunityResponse>>(
      `/donors/me/opportunities/${requestId}/respond`,
      payload
    );
    return response.data;
  },
};

export default donorService;


