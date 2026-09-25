// frontend/services/bloodBankService.ts
// LifeLink AI — Blood Bank Service
// Architecture Reference: ARCHITECTURE.md Section 27; API.md Section 9

import { apiClient } from '@/lib/api';
import type {
  BloodBank,
  BloodBankCreateData,
  BloodBankDashboardData,
  BloodBankUpdateData,
  EmergencyDemandItem,
} from '@/types';

export const bloodBankService = {
  async getMyProfile(): Promise<BloodBank> {
    const res = await apiClient.get<{ success: boolean; data: BloodBank }>('/blood-banks/me');
    return res.data.data;
  },

  async createProfile(data: BloodBankCreateData): Promise<BloodBank> {
    const res = await apiClient.post<{ success: boolean; data: BloodBank }>('/blood-banks', data);
    return res.data.data;
  },

  async updateProfile(data: BloodBankUpdateData): Promise<BloodBank> {
    const res = await apiClient.put<{ success: boolean; data: BloodBank }>('/blood-banks/me', data);
    return res.data.data;
  },

  async getDashboard(): Promise<BloodBankDashboardData> {
    const res = await apiClient.get<{ success: boolean; data: BloodBankDashboardData }>('/blood-banks/me/dashboard');
    return res.data.data;
  },

  async getEmergencyDemand(params?: { offset?: number; limit?: number }): Promise<{ items: EmergencyDemandItem[]; total: number }> {
    const res = await apiClient.get<{ success: boolean; data: { items: EmergencyDemandItem[]; total: number } }>('/blood-banks/me/demand', { params });
    return res.data.data;
  },

  async listBloodBanks(params?: { city?: string; limit?: number; offset?: number }): Promise<{ items: BloodBank[]; total: number }> {
    const res = await apiClient.get<{ success: boolean; data: { items: BloodBank[]; total: number } }>('/blood-banks', { params });
    return res.data.data;
  },

  async getMyInventory(): Promise<{ items: import('@/types').BloodInventoryItem[]; summary: import('@/types').InventorySummary }> {
    const res = await apiClient.get<{ success: boolean; data: { items: import('@/types').BloodInventoryItem[]; summary: import('@/types').InventorySummary } }>(
      '/blood-banks/me/inventory'
    );
    return res.data.data;
  },

  async updateInventoryItem(
    bloodType: string,
    data: import('@/types').BloodInventoryUpdatePayload
  ): Promise<import('@/types').BloodInventoryItem> {
    const res = await apiClient.put<{ success: boolean; data: import('@/types').BloodInventoryItem }>(
      `/blood-banks/me/inventory/${encodeURIComponent(bloodType)}`,
      data
    );
    return res.data.data;
  },

  async batchUpdateInventory(
    items: Array<import('@/types').BloodInventoryUpdatePayload & { blood_type: string }>
  ): Promise<import('@/types').BloodInventoryItem[]> {
    const res = await apiClient.put<{ success: boolean; data: import('@/types').BloodInventoryItem[] }>(
      '/blood-banks/me/inventory',
      { items }
    );
    return res.data.data;
  },

  async checkDemandAvailability(requestId: string): Promise<import('@/types').DemandAvailabilityResult> {
    const res = await apiClient.get<{ success: boolean; data: import('@/types').DemandAvailabilityResult }>(
      `/blood-banks/me/demand/${requestId}/availability`
    );
    return res.data.data;
  },

  async respondToEmergency(
    requestId: string,
    payload: { units_committed: number; blood_type?: string; status?: string; message?: string }
  ): Promise<any> {
    const res = await apiClient.post<{ success: boolean; message: string; data: any }>(
      `/blood-banks/me/demand/${requestId}/respond`,
      payload
    );
    return res.data.data;
  },

  async deleteBloodBankAccount(): Promise<any> {
    const res = await apiClient.delete<{ success: boolean; data: any }>('/blood-banks/me');
    return res.data;
  },
};
