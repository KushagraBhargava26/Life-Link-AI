// frontend/services/adminService.ts
// LifeLink AI — Admin Governance Service
// Architecture Reference: ARCHITECTURE.md Section 22

import { apiClient } from '@/lib/api';

export interface AdminFacility {
  id: string;
  name: string;
  registration_number?: string;
  license_number?: string;
  type?: string;
  city: string;
  state: string;
  phone: string;
  email?: string;
  is_24_hours?: boolean;
  license_issue_date?: string;
  license_expiry_date?: string;
  certificate_url?: string;
  status: 'ACTIVE' | 'SUSPENDED' | 'BLOCKED';
  is_verified: boolean;
  created_at: string;
}

export interface AdminFacilityListResponse {
  hospitals: AdminFacility[];
  blood_banks: AdminFacility[];
  total_active: number;
  total_suspended: number;
  total_blocked: number;
}

export const adminService = {
  async getPendingVerifications(): Promise<{
    hospitals: AdminFacility[];
    blood_banks: AdminFacility[];
    total_pending: number;
  }> {
    const res = await apiClient.get<{
      success: boolean;
      data: {
        hospitals: AdminFacility[];
        blood_banks: AdminFacility[];
        total_pending: number;
      };
    }>('/admin/verifications/pending');
    return res.data.data;
  },

  async getAllFacilities(status?: string): Promise<AdminFacilityListResponse> {
    const res = await apiClient.get<{ success: boolean; data: AdminFacilityListResponse }>('/admin/facilities', {
      params: status ? { status } : undefined,
    });
    return res.data.data;
  },

  async verifyHospital(hospitalId: string, isVerified: boolean = true): Promise<AdminFacility> {
    const res = await apiClient.patch<{ success: boolean; data: AdminFacility }>(
      `/admin/hospitals/${hospitalId}/verify`,
      { is_verified: isVerified }
    );
    return res.data.data;
  },

  async verifyBloodBank(bloodBankId: string, isVerified: boolean = true): Promise<AdminFacility> {
    const res = await apiClient.patch<{ success: boolean; data: AdminFacility }>(
      `/admin/blood-banks/${bloodBankId}/verify`,
      { is_verified: isVerified }
    );
    return res.data.data;
  },

  async updateHospitalStatus(hospitalId: string, status: string, reason?: string): Promise<AdminFacility> {
    const res = await apiClient.patch<{ success: boolean; data: AdminFacility }>(
      `/admin/hospitals/${hospitalId}/status`,
      { status, reason }
    );
    return res.data.data;
  },

  async updateBloodBankStatus(bloodBankId: string, status: string, reason?: string): Promise<AdminFacility> {
    const res = await apiClient.patch<{ success: boolean; data: AdminFacility }>(
      `/admin/blood-banks/${bloodBankId}/status`,
      { status, reason }
    );
    return res.data.data;
  },
};
