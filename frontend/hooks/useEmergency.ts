// frontend/hooks/useEmergency.ts
// LifeLink AI — Emergency Status Hook
// Architecture Reference: ARCHITECTURE.md Section 15
// Phase 1.1: Placeholder stub.

import { useEmergencyStore } from '@/store/emergencyStore';

/**
 * useEmergency — provides emergency request state and polling logic.
 * Phase 1.3+: Connect to emergency API with React Query.
 */
export function useEmergency() {
  const activeRequests = useEmergencyStore((s) => s.activeRequests);
  const currentRequest = useEmergencyStore((s) => s.currentRequest);
  const isLoading = useEmergencyStore((s) => s.isLoading);
  const setActiveRequests = useEmergencyStore((s) => s.setActiveRequests);
  const setCurrentRequest = useEmergencyStore((s) => s.setCurrentRequest);

  return {
    activeRequests,
    currentRequest,
    isLoading,
    setActiveRequests,
    setCurrentRequest,
  };
}
