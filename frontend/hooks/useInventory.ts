// frontend/hooks/useInventory.ts
// LifeLink AI — Blood Inventory Hook
// Architecture Reference: ARCHITECTURE.md Section 15
// Phase 1.1: Placeholder stub.

/**
 * useInventory — provides blood inventory data and update functions.
 * Phase 1.3+: Connect to inventory API with React Query.
 */
export function useInventory(facilityId?: string) {
  // Phase 1.3+: Implement with React Query
  // const { data, isLoading, error, refetch } = useQuery({
  //   queryKey: ['inventory', facilityId],
  //   queryFn: () => apiGet(`/inventory/${facilityId}`),
  //   refetchInterval: 120_000, // 2 min — matches cache TTL
  // });

  return {
    inventory: null,
    isLoading: false,
    error: null,
    facilityId,
  };
}
