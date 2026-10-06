// frontend/services/emergencyService.ts
// LifeLink AI — Emergency API Service
// Architecture Reference: ARCHITECTURE.md Section 15 & Section 23

import { api } from '@/lib/api';
import { ApiSuccessResponse, CreateEmergencyPayload, EmergencyRequestData } from '@/types';

export type { EmergencyRequestData };

export const emergencyService = {
  /**
   * Submit a new emergency request
   */
  async createRequest(payload: CreateEmergencyPayload): Promise<ApiSuccessResponse<EmergencyRequestData>> {
    const response = await api.post<ApiSuccessResponse<EmergencyRequestData>>('/emergency', payload);
    return response.data;
  },

  /**
   * Get an emergency request by UUID or request_number (e.g. EMR-2026-0001)
   */
  async getRequest(idOrNumber: string): Promise<ApiSuccessResponse<EmergencyRequestData>> {
    const response = await api.get<ApiSuccessResponse<EmergencyRequestData>>(`/emergency/${encodeURIComponent(idOrNumber)}`);
    return response.data;
  },

  /**
   * Get live status of an emergency request
   */
  async getStatus(idOrNumber: string): Promise<ApiSuccessResponse<{
    id: string;
    request_number: string;
    status: string;
    units_required: number;
    units_fulfilled: number;
    updated_at: string;
  }>> {
    const response = await api.get(`/emergency/${encodeURIComponent(idOrNumber)}/status`);
    return response.data;
  },

  /**
   * Get the latest GPS vehicle location for a request (Phase 1.8 telemetry)
   */
  async getLocation(idOrNumber: string): Promise<{
    success: boolean;
    data: {
      id: string;
      request_id: string;
      latitude: number;
      longitude: number;
      heading?: number;
      speed_kmh?: number;
      status_note?: string;
      recorded_at: string;
    } | null;
    message: string;
  }> {
    const response = await api.get(`/emergency/${encodeURIComponent(idOrNumber)}/location`);
    return response.data;
  },

  /**
   * Broadcast shortage to external voluntary donors and blood banks
   */
  async escalateRequest(idOrNumber: string, reason?: string): Promise<ApiSuccessResponse<EmergencyRequestData>> {
    const response = await api.post<ApiSuccessResponse<EmergencyRequestData>>(
      `/emergency/${encodeURIComponent(idOrNumber)}/escalate`,
      {},
      { params: reason ? { reason } : undefined }
    );
    return response.data;
  },
};

export default emergencyService;
