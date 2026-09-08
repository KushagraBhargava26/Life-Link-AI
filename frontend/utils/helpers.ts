// frontend/utils/helpers.ts
// LifeLink AI — Frontend Helper Functions
// Architecture Reference: ARCHITECTURE.md Section 15 (Frontend Architecture)
//
// Reusable UI/validation helpers.

/**
 * Validate coordinates
 */
export function isValidCoordinate(lat: number, lon: number): boolean {
  return lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
}

/**
 * Calculate approximate ETA based on distance assuming average city traffic speed (30 km/h)
 */
export function estimateETA(distanceKm: number): number {
  const averageSpeedKmh = 30;
  const timeHours = distanceKm / averageSpeedKmh;
  return Math.round(timeHours * 60); // ETA in minutes
}
