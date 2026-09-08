// frontend/services/matchingService.ts
// LifeLink AI — Matching & Coordination Engine API Client
// Architecture Reference: ARCHITECTURE.md ADR-004 & Section 17

import { api } from '@/lib/api';
import { ApiResponse, MatchRun, MatchCandidate, MatchCandidateStatus } from '@/types';

export const matchingService = {
  /**
   * Retrieves the latest matching recommendations for an emergency requisition.
   * If matching has not been executed yet, triggers initial run.
   */
  async getMatches(requestId: string): Promise<ApiResponse<MatchRun>> {
    const response = await api.get<ApiResponse<MatchRun>>(
      `/emergency/requests/${requestId}/matches`
    );
    return response.data;
  },

  /**
   * Executes or re-runs matching with a specific search radius (km).
   */
  async runMatching(
    requestId: string,
    searchRadiusKm: number = 50.0
  ): Promise<ApiResponse<MatchRun>> {
    const response = await api.post<ApiResponse<MatchRun>>(
      `/emergency/requests/${requestId}/match?search_radius_km=${searchRadiusKm}`
    );
    return response.data;
  },

  /**
   * Updates candidate status (SHORTLISTED, DISMISSED, PROPOSED).
   */
  async updateCandidateStatus(
    requestId: string,
    candidateId: string,
    status: MatchCandidateStatus
  ): Promise<ApiResponse<MatchCandidate>> {
    const response = await api.patch<ApiResponse<MatchCandidate>>(
      `/emergency/requests/${requestId}/matches/${candidateId}`,
      { status }
    );
    return response.data;
  },
};

export default matchingService;
