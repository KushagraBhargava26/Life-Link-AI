'use client';

// frontend/components/features/maps/EmergencyDispatchMap.tsx
// LifeLink AI — Interactive Real-Time Emergency Dispatch Map & Route ETA
// Architecture Reference: ARCHITECTURE.md Section 15 & Section 17

import React, { useEffect, useState, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Badge } from '@/components/ui/Badge';

export interface MapHospitalPoint {
  name: string;
  latitude: number;
  longitude: number;
  address?: string;
}

export interface MapCandidatePoint {
  id: string;
  name: string;
  type: 'DONOR' | 'BLOOD_BANK';
  bloodType: string;
  latitude?: number | null;
  longitude?: number | null;
  distanceKm?: number | null;
  unitsAvailable?: number | null;
  status?: string | null;
  donorResponseStatus?: string | null;
  isAccepted?: boolean;
}

export interface MapVehicleTelemetry {
  latitude: number;
  longitude: number;
  speed_kmh?: number;
  heading?: number;
  status_note?: string;
  recorded_at?: string;
}

export interface EmergencyDispatchMapProps {
  hospital: MapHospitalPoint;
  candidates?: MapCandidatePoint[];
  vehicleTelemetry?: MapVehicleTelemetry | null;
  searchRadiusKm?: number;
  zoom?: number;
  heightClassName?: string;
}

// Auto-recenter map when bounds change
function MapRecenter({ bounds }: { bounds: L.LatLngBoundsExpression }) {
  const map = useMap();
  useEffect(() => {
    if (bounds) {
      try {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
      } catch {
        // Fallback if bounds are invalid
      }
    }
  }, [bounds, map]);
  return null;
}

export function EmergencyDispatchMap({
  hospital,
  candidates = [],
  vehicleTelemetry = null,
  searchRadiusKm = 50,
  zoom = 12,
  heightClassName = 'h-[420px]',
}: EmergencyDispatchMapProps) {
  const [isMounted, setIsMounted] = useState<boolean>(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Filter candidates with valid geographical coordinates
  const geoCandidates = useMemo(() => {
    return candidates.filter(
      (c) => c.latitude !== null && c.latitude !== undefined && c.longitude !== null && c.longitude !== undefined
    ) as (MapCandidatePoint & { latitude: number; longitude: number })[];
  }, [candidates]);

  // Find primary active route point (accepted donor or vehicle telemetry or highest ranked candidate)
  const activeRoutePoint = useMemo(() => {
    if (vehicleTelemetry) {
      return {
        lat: vehicleTelemetry.latitude,
        lng: vehicleTelemetry.longitude,
        label: 'Active Courier / Vehicle',
        distanceKm: null,
      };
    }
    const accepted = geoCandidates.find((c) => c.isAccepted || c.donorResponseStatus === 'ACCEPTED');
    if (accepted) {
      return {
        lat: accepted.latitude,
        lng: accepted.longitude,
        label: `${accepted.name} (${accepted.bloodType})`,
        distanceKm: accepted.distanceKm,
      };
    }
    if (geoCandidates.length > 0) {
      const top = geoCandidates[0];
      return {
        lat: top.latitude,
        lng: top.longitude,
        label: `${top.name} (${top.bloodType})`,
        distanceKm: top.distanceKm,
      };
    }
    return null;
  }, [geoCandidates, vehicleTelemetry]);

  // Compute calculated emergency route ETA (assuming ~35 km/h urban emergency response transit)
  const routeEta = useMemo(() => {
    if (!activeRoutePoint) return null;
    let dist = activeRoutePoint.distanceKm;

    if (dist === null || dist === undefined) {
      // Haversine approximation
      const R = 6371;
      const dLat = ((activeRoutePoint.lat - hospital.latitude) * Math.PI) / 180;
      const dLon = ((activeRoutePoint.lng - hospital.longitude) * Math.PI) / 180;
      const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos((hospital.latitude * Math.PI) / 180) *
          Math.cos((activeRoutePoint.lat * Math.PI) / 180) *
          Math.sin(dLon / 2) *
          Math.sin(dLon / 2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      dist = Math.round(R * c * 10) / 10;
    }

    const minutes = Math.max(4, Math.round((dist / 35) * 60));
    return {
      distanceKm: dist,
      estimatedMinutes: minutes,
      speedText: vehicleTelemetry?.speed_kmh ? `${vehicleTelemetry.speed_kmh} km/h` : 'Est. 35 km/h transit',
    };
  }, [activeRoutePoint, hospital, vehicleTelemetry]);

  // Create custom marker icons
  const hospitalIcon = useMemo(() => {
    return L.divIcon({
      className: 'custom-map-icon',
      html: `
        <div style="
          background: #C9193A;
          color: white;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 18px;
          box-shadow: 0 0 0 5px rgba(201, 25, 58, 0.25), 0 4px 10px rgba(0,0,0,0.3);
          border: 2px solid white;
        ">🏥</div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 18],
    });
  }, []);

  const donorIcon = useMemo(() => {
    return (bloodType: string, isAccepted: boolean) =>
      L.divIcon({
        className: 'custom-map-icon',
        html: `
          <div style="
            background: ${isAccepted ? '#16845B' : '#E11D48'};
            color: white;
            padding: 2px 7px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 3px;
            border: 2px solid white;
            box-shadow: 0 0 0 3px ${isAccepted ? 'rgba(22, 132, 91, 0.3)' : 'rgba(225, 29, 72, 0.25)'}, 0 2px 8px rgba(0,0,0,0.25);
            white-space: nowrap;
          ">
            <span>🩸</span><span>${bloodType}</span>
          </div>
        `,
        iconSize: [44, 24],
        iconAnchor: [22, 12],
      });
  }, []);

  const bloodBankIcon = useMemo(() => {
    return L.divIcon({
      className: 'custom-map-icon',
      html: `
        <div style="
          background: #2563EB;
          color: white;
          width: 32px;
          height: 32px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 16px;
          border: 2px solid white;
          box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.25), 0 3px 8px rgba(0,0,0,0.25);
        ">🏢</div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    });
  }, []);

  const vehicleIcon = useMemo(() => {
    return L.divIcon({
      className: 'custom-map-icon',
      html: `
        <div style="
          background: #10B981;
          color: white;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          border: 2px solid white;
          animation: pulse 1.5s infinite;
          box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.35), 0 4px 10px rgba(0,0,0,0.3);
        ">🚑</div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 18],
    });
  }, []);

  if (!isMounted) {
    return (
      <div className={`w-full ${heightClassName} rounded-xl bg-card border border-border flex flex-col items-center justify-center gap-2 text-muted-foreground`}>
        <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin" />
        <span className="text-xs font-medium">Loading interactive dispatch map...</span>
      </div>
    );
  }

  // Calculate map bounds
  const allPoints: [number, number][] = [[hospital.latitude, hospital.longitude]];
  geoCandidates.forEach((c) => allPoints.push([c.latitude, c.longitude]));
  if (vehicleTelemetry) {
    allPoints.push([vehicleTelemetry.latitude, vehicleTelemetry.longitude]);
  }

  return (
    <div className={`relative w-full ${heightClassName} rounded-xl overflow-hidden border border-border shadow-sm`}>
      {/* Route & ETA Telemetry Overlay Badge */}
      {routeEta && (
        <div className="absolute top-3 left-3 z-[1000] bg-card/95 backdrop-blur-md border border-border/80 px-3.5 py-2.5 rounded-xl shadow-lg max-w-xs text-foreground flex flex-col gap-1">
          <div className="flex items-center justify-between gap-3">
            <span className="text-xs font-bold text-primary flex items-center gap-1.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
              </span>
              Emergency Dispatch ETA
            </span>
            <Badge variant="success" size="sm" className="font-mono font-bold">
              ~{routeEta.estimatedMinutes} mins
            </Badge>
          </div>
          <div className="text-[11px] text-muted-foreground flex items-center justify-between gap-3 pt-0.5">
            <span>Route: <strong>{routeEta.distanceKm} km</strong></span>
            <span>Speed: <strong>{routeEta.speedText}</strong></span>
          </div>
          {activeRoutePoint && (
            <p className="text-[10px] text-muted-foreground truncate pt-0.5 border-t border-border/50">
              Target: <strong className="text-foreground">{activeRoutePoint.label}</strong>
            </p>
          )}
        </div>
      )}

      {/* Map Layers Legend */}
      <div className="absolute bottom-3 right-3 z-[1000] bg-card/90 backdrop-blur-md border border-border px-3 py-1.5 rounded-lg shadow-sm text-[11px] flex items-center gap-3 text-muted-foreground">
        <span className="flex items-center gap-1">🏥 Hospital</span>
        <span className="flex items-center gap-1">🩸 Donor</span>
        <span className="flex items-center gap-1">🏢 Blood Bank</span>
        {vehicleTelemetry && <span className="flex items-center gap-1">🚑 Courier</span>}
      </div>

      <MapContainer
        center={[hospital.latitude, hospital.longitude]}
        zoom={zoom}
        scrollWheelZoom={false}
        className="w-full h-full z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {allPoints.length > 1 && <MapRecenter bounds={allPoints} />}

        {/* Search radius circle around hospital */}
        <Circle
          center={[hospital.latitude, hospital.longitude]}
          radius={searchRadiusKm * 1000}
          pathOptions={{
            color: '#C9193A',
            fillColor: '#C9193A',
            fillOpacity: 0.05,
            weight: 1.5,
            dashArray: '5, 5',
          }}
        />

        {/* Hospital Destination Marker */}
        <Marker position={[hospital.latitude, hospital.longitude]} icon={hospitalIcon}>
          <Popup>
            <div className="p-1 space-y-1 text-xs">
              <strong className="text-primary block text-sm">{hospital.name}</strong>
              <p className="text-muted-foreground">Destination Emergency Facility</p>
              {hospital.address && <p className="text-[11px]">{hospital.address}</p>}
            </div>
          </Popup>
        </Marker>

        {/* Candidates Markers */}
        {geoCandidates.map((cand) => {
          const isAccepted = cand.isAccepted || cand.donorResponseStatus === 'ACCEPTED';
          return (
            <Marker
              key={cand.id}
              position={[cand.latitude, cand.longitude]}
              icon={
                cand.type === 'DONOR'
                  ? donorIcon(cand.bloodType, isAccepted)
                  : bloodBankIcon
              }
            >
              <Popup>
                <div className="p-1 space-y-1 text-xs">
                  <strong className="block text-sm">{cand.name}</strong>
                  <p>Type: <strong>{cand.type === 'DONOR' ? 'Voluntary Donor' : 'Verified Blood Bank'}</strong></p>
                  <p>Blood Group: <strong className="text-primary">{cand.bloodType}</strong></p>
                  {cand.distanceKm !== null && cand.distanceKm !== undefined && (
                    <p>Distance: <strong>{cand.distanceKm.toFixed(1)} km</strong></p>
                  )}
                  {cand.unitsAvailable && <p>Stock Available: <strong>{cand.unitsAvailable} Units</strong></p>}
                  {cand.status && <p>Triage Status: <strong>{cand.status}</strong></p>}
                  {cand.donorResponseStatus && (
                    <p>Response: <strong className={isAccepted ? 'text-success' : 'text-primary'}>{cand.donorResponseStatus}</strong></p>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Live Courier / Vehicle Telemetry Marker */}
        {vehicleTelemetry && (
          <Marker position={[vehicleTelemetry.latitude, vehicleTelemetry.longitude]} icon={vehicleIcon}>
            <Popup>
              <div className="p-1 space-y-1 text-xs">
                <strong className="text-success block text-sm">🚑 Blood Dispatch in Transit</strong>
                {vehicleTelemetry.speed_kmh !== undefined && (
                  <p>Speed: <strong>{vehicleTelemetry.speed_kmh} km/h</strong></p>
                )}
                {vehicleTelemetry.status_note && <p>{vehicleTelemetry.status_note}</p>}
              </div>
            </Popup>
          </Marker>
        )}

        {/* Polyline Route from Active Source to Hospital */}
        {activeRoutePoint && (
          <Polyline
            positions={[
              [activeRoutePoint.lat, activeRoutePoint.lng],
              [hospital.latitude, hospital.longitude],
            ]}
            pathOptions={{
              color: '#16845B',
              weight: 3.5,
              dashArray: '6, 6',
              opacity: 0.85,
            }}
          />
        )}
      </MapContainer>
    </div>
  );
}
export default EmergencyDispatchMap;
