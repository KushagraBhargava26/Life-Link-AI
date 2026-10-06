// frontend/lib/geolocation.ts
// LifeLink AI — Geolocation & Reverse Geocoding Services
// Provides browser GPS access, OpenStreetMap Nominatim reverse geocoding, and distance calculations

export interface GeocodedAddress {
  latitude: number;
  longitude: number;
  address_line: string;
  city: string;
  state: string;
  pincode: string;
  country: string;
  display_name: string;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
  accuracy?: number;
}

/**
 * Requests GPS coordinates from the user's browser.
 */
export async function getBrowserLocation(): Promise<Coordinates> {
  if (typeof window === 'undefined' || !navigator.geolocation) {
    throw new Error('Geolocation is not supported by your browser.');
  }

  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
        });
      },
      (error) => {
        switch (error.code) {
          case error.PERMISSION_DENIED:
            reject(new Error('Location permission denied. Please allow location access in your browser settings.'));
            break;
          case error.POSITION_UNAVAILABLE:
            reject(new Error('Location information is unavailable. Please try manual entry.'));
            break;
          case error.TIMEOUT:
            reject(new Error('Location request timed out. Please try again.'));
            break;
          default:
            reject(new Error(error.message || 'An unknown error occurred while detecting location.'));
            break;
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      }
    );
  });
}

/**
 * Reverse geocodes latitude and longitude into address, city, state, and pincode via OpenStreetMap Nominatim.
 */
export async function reverseGeocodeNominatim(lat: number, lon: number): Promise<GeocodedAddress> {
  try {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&zoom=18&addressdetails=1`;
    const response = await fetch(url, {
      headers: {
        'Accept-Language': 'en',
      },
    });

    if (!response.ok) {
      throw new Error(`Geocoding failed with status: ${response.status}`);
    }

    const data = await response.json();
    const addr = data.address || {};

    const city =
      addr.city ||
      addr.town ||
      addr.city_district ||
      addr.suburb ||
      addr.municipality ||
      addr.county ||
      addr.village ||
      '';

    const state = addr.state || addr.region || addr.province || '';
    const pincode = addr.postcode || '';
    
    const addressParts = [
      addr.house_number,
      addr.building,
      addr.road,
      addr.neighbourhood || addr.suburb,
    ].filter(Boolean);

    const address_line = addressParts.length > 0 ? addressParts.join(', ') : (data.display_name?.split(',').slice(0, 2).join(',') || '');
    const country = addr.country || '';

    return {
      latitude: lat,
      longitude: lon,
      address_line,
      city,
      state,
      pincode,
      country,
      display_name: data.display_name || `${city}, ${state}`,
    };
  } catch (err: any) {
    // Return coordinates with fallback if service is temporarily unavailable
    return {
      latitude: lat,
      longitude: lon,
      address_line: '',
      city: '',
      state: '',
      pincode: '',
      country: '',
      display_name: `Lat: ${lat.toFixed(4)}, Lon: ${lon.toFixed(4)}`,
    };
  }
}

/**
 * Calculates the great-circle distance between two GPS coordinates using the Haversine formula (in kilometers).
 */
export function calculateHaversineDistanceKm(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371; // Earth's mean radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Number((R * c).toFixed(1));
}
