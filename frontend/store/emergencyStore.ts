// frontend/store/emergencyStore.ts
// LifeLink AI — Zustand Emergency Request Store
// Architecture Reference: ARCHITECTURE.md Section 15 (State Management)
//
// Manages global state related to active emergency requests and live updates.

import { create } from 'zustand';
import { EmergencyRequest } from '@/types';

interface EmergencyState {
  activeRequests: EmergencyRequest[];
  currentRequest: EmergencyRequest | null;
  isLoading: boolean;

  // Actions
  setActiveRequests: (requests: EmergencyRequest[]) => void;
  setCurrentRequest: (request: EmergencyRequest | null) => void;
  addRequest: (request: EmergencyRequest) => void;
  updateRequestStatus: (requestId: string, status: EmergencyRequest['status']) => void;
  setLoading: (isLoading: boolean) => void;
}

export const useEmergencyStore = create<EmergencyState>((set) => ({
  activeRequests: [],
  currentRequest: null,
  isLoading: false,

  setActiveRequests: (requests) => set({ activeRequests: requests }),
  setCurrentRequest: (request) => set({ currentRequest: request }),
  
  addRequest: (request) =>
    set((state) => ({
      activeRequests: [request, ...state.activeRequests],
    })),

  updateRequestStatus: (requestId, status) =>
    set((state) => ({
      activeRequests: state.activeRequests.map((req) =>
        req.id === requestId ? { ...req, status } : req
      ),
      currentRequest:
        state.currentRequest?.id === requestId
          ? { ...state.currentRequest, status }
          : state.currentRequest,
    })),

  setLoading: (isLoading) => set({ isLoading }),
}));
