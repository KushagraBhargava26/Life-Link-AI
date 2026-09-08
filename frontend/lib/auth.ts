// frontend/lib/auth.ts
// LifeLink AI — Authentication Helpers
// Architecture Reference: ARCHITECTURE.md Section 15 & Section 18
//
// Reusable client-side helpers for authentication, cookie parsing,
// and checking user roles/permissions.

import { UserRole } from '@/types';

/**
 * Checks if a user role matches any of the allowed roles.
 */
export function hasRole(userRole: UserRole | undefined, allowedRoles: UserRole[]): boolean {
  if (!userRole) return false;
  return allowedRoles.includes(userRole);
}

/**
 * Determines if a user role has administrative access.
 */
export function isAdmin(role: UserRole | undefined): boolean {
  return hasRole(role, ['SUPER_ADMIN', 'ADMIN']);
}

/**
 * Determines if a user role belongs to a hospital staff member.
 */
export function isHospitalStaff(role: UserRole | undefined): boolean {
  return hasRole(role, ['HOSPITAL_ADMIN', 'HOSPITAL_STAFF']);
}

/**
 * Determines if a user role belongs to a blood bank operator.
 */
export function isBloodBankStaff(role: UserRole | undefined): boolean {
  return hasRole(role, ['BLOOD_BANK_MANAGER', 'BLOOD_BANK_STAFF']);
}

/**
 * Determines if a user role is a donor.
 */
export function isDonor(role: UserRole | undefined): boolean {
  return hasRole(role, ['DONOR']);
}

/**
 * Resolves the primary role for a user.
 */
export function getPrimaryRole(user: any): UserRole {
  if (!user) return 'DONOR';
  if (user.role) return user.role as UserRole;
  if (user.roles && Array.isArray(user.roles) && user.roles.length > 0) {
    return user.roles[0] as UserRole;
  }
  return 'DONOR';
}

/**
 * Resolves the default dashboard URL for a user based on primary role.
 */
export function getDefaultDashboardPath(user: any): string {
  const role = getPrimaryRole(user);
  if (isAdmin(role)) return '/admin';
  if (isHospitalStaff(role)) return '/hospital';
  if (isBloodBankStaff(role)) return '/blood-bank';
  if (isDonor(role)) return '/donor';
  return '/dashboard';
}

/**
 * Decodes client-side JWT token (without verifying signature).
 * Used purely for reading metadata like expiry and role.
 */
export function parseJwt(token: string) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    return null;
  }
}
