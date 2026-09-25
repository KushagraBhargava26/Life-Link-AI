// frontend/services/hospitalService.ts
// LifeLink AI — Hospital Service
// Architecture Reference: ARCHITECTURE.md Section 27; API.md Section 8

import { apiClient } from '@/lib/api';
import type {
  Hospital,
  HospitalCreateData,
  HospitalDashboardData,
  HospitalUpdateData,
} from '@/types';

export const hospitalService = {
  async getMyProfile(): Promise<Hospital> {
    const res = await apiClient.get<{ success: boolean; data: Hospital }>('/hospitals/me');
    return res.data.data;
  },

  async createProfile(data: HospitalCreateData): Promise<Hospital> {
    const res = await apiClient.post<{ success: boolean; data: Hospital }>('/hospitals', data);
    return res.data.data;
  },

  async updateProfile(data: HospitalUpdateData): Promise<Hospital> {
    const res = await apiClient.put<{ success: boolean; data: Hospital }>('/hospitals/me', data);
    return res.data.data;
  },

  async getDashboard(): Promise<HospitalDashboardData> {
    const res = await apiClient.get<{ success: boolean; data: HospitalDashboardData }>('/hospitals/me/dashboard');
    return res.data.data;
  },

  async getRequests(params?: { offset?: number; limit?: number }): Promise<{ items: any[]; total: number }> {
    const res = await apiClient.get<{ success: boolean; data: { items: any[]; total: number } }>('/hospitals/me/requests', { params });
    return res.data.data;
  },

  async createEmergencyRequest(data: {
    blood_type: string;
    units_required: number;
    urgency_level: string;
    patient_name?: string;
    patient_age?: number;
    notes?: string;
    facility_address?: string;
  }): Promise<any> {
    const res = await apiClient.post<{ success: boolean; data: any }>('/hospitals/me/requests', data);
    return res.data.data;
  },

  async listHospitals(params?: { city?: string; limit?: number; offset?: number }): Promise<{ items: Hospital[]; total: number }> {
    const res = await apiClient.get<{ success: boolean; data: { items: Hospital[]; total: number } }>('/hospitals', { params });
    return res.data.data;
  },

  async deleteHospitalAccount(): Promise<any> {
    const res = await apiClient.delete<{ success: boolean; data: any }>('/hospitals/me');
    return res.data;
  },
};
