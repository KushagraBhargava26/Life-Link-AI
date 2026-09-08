// frontend/services/apiService.ts
// LifeLink AI — API Service Scaffold
// Architecture Reference: ARCHITECTURE.md Section 15 (Frontend Architecture)
//
// Placeholder service scaffold. Put all standard API call logic here in future phases.

import { api } from '@/lib/api';
import { ApiSuccessResponse } from '@/types';

export const apiService = {
  // Placeholder get status method
  async getStatus(): Promise<ApiSuccessResponse<{ status: string }>> {
    const response = await api.get('/health');
    return response.data;
  },
};
export default apiService;
