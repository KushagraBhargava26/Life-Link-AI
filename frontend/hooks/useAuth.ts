// frontend/hooks/useAuth.ts
// LifeLink AI — Auth Custom Hook
// Architecture Reference: ARCHITECTURE.md Section 15
// Principle: "Business logic lives in custom hooks"

import { useAuthStore } from '@/store/authStore';

/**
 * useAuth — provides auth state and actions to components.
 * Phase 1.1: Placeholder — returns store state only.
 * Phase 1.3+: Add login(), logout(), refreshToken() implementations.
 */
export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const accessToken = useAuthStore((s) => s.accessToken);
  const setAuth = useAuthStore((s) => s.setAuth);
  const clearAuth = useAuthStore((s) => s.clearAuth);

  return {
    user,
    isAuthenticated,
    isLoading,
    accessToken,
    setAuth,
    clearAuth,
  };
}
