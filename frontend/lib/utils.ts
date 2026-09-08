// frontend/lib/utils.ts
// LifeLink AI — Frontend UI Utilities
// Architecture Reference: ARCHITECTURE.md Section 15 (Frontend Architecture)

import { type ClassValue, clsx } from 'clsx';

/**
 * Combines Tailwind classes conditionally and returns a clean string.
 * Uses clsx for resolving arrays/objects.
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

/**
 * Standard formatter for dates.
 */
export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (error) {
    return dateString;
  }
}

/**
 * Format blood type for display based on ABO/Rh properties.
 */
export function formatBloodType(aboGroup: string, rhPositive: boolean): string {
  return `${aboGroup}${rhPositive ? '+' : '-'}`;
}
