'use client';

// frontend/components/ui/LocationDetector.tsx
// LifeLink AI — One-click GPS Location Detector & Reverse Geocoder

import React, { useState } from 'react';
import { Button } from './Button';
import { getBrowserLocation, reverseGeocodeNominatim, GeocodedAddress } from '@/lib/geolocation';

interface LocationDetectorProps {
  onLocationDetected: (location: GeocodedAddress) => void;
  currentCoordinates?: { latitude?: number | null; longitude?: number | null };
  className?: string;
  buttonText?: string;
}

export function LocationDetector({
  onLocationDetected,
  currentCoordinates,
  className = '',
  buttonText = 'Auto-Detect Current Location (GPS)',
}: LocationDetectorProps) {
  const [isLocating, setIsLocating] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [lastDetected, setLastDetected] = useState<GeocodedAddress | null>(null);

  const handleDetectLocation = async () => {
    setIsLocating(true);
    setErrorMsg(null);

    try {
      // 1. Get browser GPS position
      const coords = await getBrowserLocation();

      // 2. Reverse geocode via OpenStreetMap Nominatim
      const geocoded = await reverseGeocodeNominatim(coords.latitude, coords.longitude);

      setLastDetected(geocoded);
      onLocationDetected(geocoded);
    } catch (err: any) {
      setErrorMsg(err.message || 'Could not fetch your location. Please enter your address details manually.');
    } finally {
      setIsLocating(false);
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex flex-wrap items-center gap-3">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleDetectLocation}
          isLoading={isLocating}
          className="flex items-center gap-1.5 border-primary/40 text-primary hover:bg-primary/10 transition-colors font-medium text-xs"
        >
          <span>📍</span>
          <span>{isLocating ? 'Detecting GPS...' : buttonText}</span>
        </Button>

        {lastDetected && (
          <span className="text-xs text-green-700 dark:text-green-400 font-medium flex items-center gap-1">
            ✓ Location detected: {lastDetected.city || lastDetected.state || 'GPS Coordinates Set'} ({lastDetected.latitude.toFixed(4)}°, {lastDetected.longitude.toFixed(4)}°)
          </span>
        )}

        {!lastDetected && currentCoordinates?.latitude != null && currentCoordinates?.longitude != null && (
          <span className="text-xs text-muted-foreground flex items-center gap-1">
            📍 Coordinates saved: ({Number(currentCoordinates.latitude).toFixed(4)}°, {Number(currentCoordinates.longitude).toFixed(4)}°)
          </span>
        )}
      </div>

      {errorMsg && (
        <div className="rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 p-2.5 text-xs text-amber-800 dark:text-amber-200 flex items-start justify-between gap-2">
          <span>⚠️ {errorMsg}</span>
          <button
            type="button"
            onClick={() => setErrorMsg(null)}
            className="text-amber-600 hover:text-amber-800 dark:hover:text-amber-100 shrink-0 font-bold"
            aria-label="Dismiss error"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}
