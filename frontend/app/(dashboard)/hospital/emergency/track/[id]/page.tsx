'use client';

// frontend/app/(dashboard)/hospital/emergency/track/[id]/page.tsx
// LifeLink AI — Hospital Real-Time Live Emergency Dispatch Corridor Tracker

import React, { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { emergencyService } from '@/services/emergencyService';
import { EmergencyRequestData } from '@/types';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

// ── Real Road Waypoints: Kurla Blood Bank → Lilavati Hospital Bandra ──
const ROUTE: [number, number][] = [
  [19.0725, 72.8710], // Kurla Regional Blood Reserve (Dispatch Origin)
  [19.0700, 72.8640], // SCLR Flyover Entry
  [19.0665, 72.8555], // BKC Connector
  [19.0620, 72.8460], // Kalanagar Junction
  [19.0575, 72.8380], // Bandra Western Express Highway
  [19.0540, 72.8330], // Hill Road Junction
  [19.0518, 72.8290], // Lilavati Hospital (Destination)
];

function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number) {
  const R = 6371;
  const toRad = (v: number) => (v * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function bearing(lat1: number, lon1: number, lat2: number, lon2: number) {
  const toRad = (v: number) => (v * Math.PI) / 180;
  const y = Math.sin(toRad(lon2 - lon1)) * Math.cos(toRad(lat2));
  const x = Math.cos(toRad(lat1)) * Math.sin(toRad(lat2)) - Math.sin(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.cos(toRad(lon2 - lon1));
  return ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360;
}

// ══════════════════════════════════════════════════════════════════════════════
// LIVE TRACKER MAP (Zomato / Uber Eats Style)
// ══════════════════════════════════════════════════════════════════════════════
function LiveTracker({
  requestId,
  hospitalName,
  hospitalLat,
  hospitalLng,
  bloodType,
  units,
  requestStatus,
  onStatusChange,
}: {
  requestId: string;
  hospitalName?: string;
  hospitalLat?: number | null;
  hospitalLng?: number | null;
  bloodType?: string;
  units?: number;
  requestStatus: string;
  onStatusChange: (newStatus: string, fulfilledUnits: number) => void;
}) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapObj = useRef<any>(null);
  const vehicleM = useRef<any>(null);
  const hospitalM = useRef<any>(null);
  const originM = useRef<any>(null);
  const traveledLine = useRef<any>(null);
  const remainingLine = useRef<any>(null);
  const stepRef = useRef(0);

  const [mapReady, setMapReady] = useState(false);
  const [pos, setPos] = useState<[number, number]>(ROUTE[0]);
  const [hdg, setHdg] = useState(250);
  const [speed, setSpeed] = useState(0);
  const [eta, setEta] = useState(9);
  const [distKm, setDistKm] = useState(4.2);
  const [progress, setProgress] = useState(0);
  const [note, setNote] = useState('Matching & Allocating Blood Reserve Inventory...');
  const [simActive, setSimActive] = useState(true);
  const [ping, setPing] = useState('Live · 2s refresh');
  const [phase, setPhase] = useState<'MATCHING' | 'PICKUP' | 'IN_TRANSIT' | 'DELIVERED'>('MATCHING');

  const destCoord = useMemo<[number, number]>(
    () => [hospitalLat || ROUTE[ROUTE.length - 1][0], hospitalLng || ROUTE[ROUTE.length - 1][1]],
    [hospitalLat, hospitalLng]
  );
  const originCoord: [number, number] = ROUTE[0];

  // ── Init Leaflet map once ──
  useEffect(() => {
    if (mapReady || !mapRef.current) return;

    const boot = () => {
      const L = (window as any).L;
      if (!L || !mapRef.current || mapObj.current) return;

      const map = L.map(mapRef.current, { center: [19.062, 72.85], zoom: 13, zoomControl: false });
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · LifeLink AI',
        maxZoom: 19,
      }).addTo(map);
      L.control.zoom({ position: 'bottomright' }).addTo(map);

      // Hospital marker
      hospitalM.current = L.marker(destCoord, {
        icon: L.divIcon({
          className: '',
          html: `<div style="display:flex;flex-direction:column;align-items:center;transform:translateX(-50%);">
            <div style="background:#dc2626;color:#fff;padding:4px 10px;border-radius:8px;font-size:11px;font-weight:800;white-space:nowrap;box-shadow:0 4px 14px rgba(220,38,38,.5);border:1.5px solid rgba(255,255,255,.6);">🏥 ${hospitalName || 'Destination Hospital'}</div>
            <div style="width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-top:8px solid #dc2626;margin-top:-1px;"></div>
          </div>`,
          iconSize: [160, 48],
          iconAnchor: [80, 48],
        }),
      }).addTo(map);

      // Origin marker
      originM.current = L.marker(originCoord, {
        icon: L.divIcon({
          className: '',
          html: `<div style="display:flex;flex-direction:column;align-items:center;transform:translateX(-50%);">
            <div style="background:#2563eb;color:#fff;padding:4px 10px;border-radius:8px;font-size:11px;font-weight:800;white-space:nowrap;box-shadow:0 4px 14px rgba(37,99,235,.5);border:1.5px solid rgba(255,255,255,.6);">🩸 Blood Reserve</div>
            <div style="width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-top:8px solid #2563eb;margin-top:-1px;"></div>
          </div>`,
          iconSize: [140, 48],
          iconAnchor: [70, 48],
        }),
      }).addTo(map);

      // Route lines
      traveledLine.current = L.polyline([originCoord, ROUTE[0]], {
        color: '#10b981', weight: 6, opacity: 1,
      }).addTo(map);
      remainingLine.current = L.polyline([ROUTE[0], destCoord], {
        color: '#ef4444', weight: 5, opacity: 0.85, dashArray: '12 8',
      }).addTo(map);

      // Vehicle marker
      vehicleM.current = L.marker(ROUTE[0], {
        icon: makeVehicleIcon(250),
        zIndexOffset: 1000,
      }).addTo(map);

      // Fit bounds
      map.fitBounds(L.featureGroup([hospitalM.current, originM.current, vehicleM.current]).getBounds().pad(0.18));

      mapObj.current = map;
      setMapReady(true);
    };

    if ((window as any).L) { boot(); return; }
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    document.head.appendChild(link);
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.onload = boot;
    document.head.appendChild(script);
  }, [mapReady, destCoord, hospitalName]);

  function makeVehicleIcon(deg: number) {
    const L = (window as any).L;
    if (!L) return null;
    return L.divIcon({
      className: '',
      html: `<style>@keyframes ll-sonar{0%{transform:scale(.6);opacity:.85}100%{transform:scale(2.8);opacity:0}}</style>
        <div style="position:relative;width:60px;height:60px;display:flex;align-items:center;justify-content:center;">
          <div style="position:absolute;width:54px;height:54px;border-radius:50%;background:rgba(239,68,68,.2);animation:ll-sonar 2s infinite ease-out;"></div>
          <div style="position:absolute;width:40px;height:40px;border-radius:50%;background:rgba(239,68,68,.35);animation:ll-sonar 2s infinite ease-out .5s;"></div>
          <div style="position:relative;width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#ef4444,#b91c1c);border:3.5px solid #fff;box-shadow:0 4px 18px rgba(0,0,0,.4);display:flex;align-items:center;justify-content:center;font-size:20px;transform:rotate(${deg}deg);transition:transform .3s ease;">
            🚑
          </div>
        </div>`,
      iconSize: [60, 60],
      iconAnchor: [30, 30],
    });
  }

  // ── Realistic Lifecycle Simulation Loop ──
  useEffect(() => {
    if (!simActive) return;
    const TOTAL = 80;

    const id = setInterval(() => {
      stepRef.current += 1;
      const step = stepRef.current;

      if (step < 6) {
        setPhase('MATCHING');
        setSpeed(0);
        setNote('Searching nearest compatible Blood Reserve & verifying cold-chain units...');
        setPing(`Live · ${new Date().toLocaleTimeString()}`);
        onStatusChange('MATCHING', 0);
      } else if (step >= 6 && step < 14) {
        setPhase('PICKUP');
        setSpeed(0);
        setPos(ROUTE[0]);
        setNote('Rider Rajesh Patil arrived at Kurla Blood Reserve · Loading thermal consignment...');
        setPing(`Live · ${new Date().toLocaleTimeString()}`);
        onStatusChange('DISPATCHED', 0);
      } else if (step >= 14 && step < TOTAL) {
        setPhase('IN_TRANSIT');
        const ratio = (step - 14) / (TOTAL - 14);
        const segs = ROUTE.length - 1;
        const si = Math.min(Math.floor(ratio * segs), segs - 1);
        const sp = ratio * segs - si;
        const p1 = ROUTE[si], p2 = ROUTE[si + 1];
        const lat = p1[0] + (p2[0] - p1[0]) * sp;
        const lng = p1[1] + (p2[1] - p1[1]) * sp;
        const newPos: [number, number] = [lat, lng];
        const hdgVal = Math.round(bearing(p1[0], p1[1], p2[0], p2[1]));
        const dist = haversineKm(lat, lng, destCoord[0], destCoord[1]);
        const spd = 42 + Math.sin(step * 0.3) * 8;

        setPos(newPos);
        setHdg(hdgVal);
        setSpeed(Math.round(spd));
        setDistKm(parseFloat(dist.toFixed(1)));
        setEta(Math.max(1, Math.round((dist / spd) * 60)));
        setProgress(Math.round(ratio * 100));
        setNote('Green Corridor Active · Emergency transit in progress');
        setPing(`Live · ${new Date().toLocaleTimeString()}`);
        onStatusChange('IN_TRANSIT', 0);
      } else if (step >= TOTAL) {
        setPhase('DELIVERED');
        setPos(destCoord);
        setSpeed(0);
        setDistKm(0);
        setEta(0);
        setProgress(100);
        setNote('✅ Consignment Handed Over to Hospital ICU Transfusion Team!');
        setPing('Live · Delivery Complete');
        onStatusChange('FULFILLED', units || 2);
      }
    }, 900);

    return () => clearInterval(id);
  }, [simActive, destCoord, units, onStatusChange]);

  useEffect(() => {
    if (!mapReady || !vehicleM.current || !(window as any).L) return;
    vehicleM.current.setLatLng(pos);
    const icon = makeVehicleIcon(hdg);
    if (icon) vehicleM.current.setIcon(icon);
    traveledLine.current?.setLatLngs([originCoord, pos]);
    remainingLine.current?.setLatLngs([pos, destCoord]);
  }, [pos, hdg, mapReady, destCoord]);

  const recenter = () => mapObj.current?.panTo(pos, { animate: true, duration: 0.5 });
  const fitAll = () => {
    if (mapObj.current && (window as any).L) {
      const L = (window as any).L;
      mapObj.current.fitBounds(
        L.featureGroup([vehicleM.current, hospitalM.current, originM.current]).getBounds().pad(0.18)
      );
    }
  };

  const restartSimulation = () => {
    stepRef.current = 0;
    setSimActive(true);
  };

  return (
    <div className="space-y-0">
      <Card className="border border-border/60 shadow-2xl bg-card overflow-hidden">
        <div className={`relative transition-colors duration-500 px-5 py-4 text-white ${
          phase === 'DELIVERED'
            ? 'bg-gradient-to-r from-emerald-600 via-teal-600 to-green-600'
            : phase === 'MATCHING'
            ? 'bg-gradient-to-r from-amber-600 via-orange-500 to-red-600'
            : 'bg-gradient-to-r from-red-600 via-rose-500 to-orange-500'
        }`}>
          <div className="absolute inset-0 bg-white/5 pointer-events-none" />
          <div className="relative flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="relative flex h-3.5 w-3.5 flex-shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-70" />
                <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-white" />
              </span>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-black text-sm tracking-wider uppercase">Hospital Dispatch Corridor</span>
                  <span className="bg-white/25 border border-white/30 text-white text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wide">
                    {phase}
                  </span>
                </div>
                <p className="text-xs text-white/90 mt-0.5 font-medium">{note}</p>
              </div>
            </div>

            <div className="text-right flex-shrink-0">
              <div className="text-[10px] uppercase font-semibold text-white/70 tracking-widest">
                {phase === 'DELIVERED' ? 'Status' : 'Estimated Arrival'}
              </div>
              <div className="text-3xl font-black tracking-tight leading-none mt-0.5">
                {phase === 'DELIVERED' ? 'ARRIVED' : `${eta} min`}
              </div>
            </div>
          </div>
        </div>

        <div className="relative">
          <div ref={mapRef} style={{ height: '440px', width: '100%', background: '#f1f5f9' }} />

          <div className="absolute top-3 left-3 z-[999] flex items-stretch gap-0 rounded-xl overflow-hidden shadow-xl border border-white/60 dark:border-zinc-700/60 bg-white/95 dark:bg-zinc-900/95 backdrop-blur-sm text-xs font-bold">
            <div className="px-3.5 py-2.5 flex flex-col items-center border-r border-border/40">
              <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Speed</span>
              <span className="text-foreground text-sm font-black mt-0.5">{speed} <span className="text-[10px] font-semibold text-muted-foreground">km/h</span></span>
            </div>
            <div className="px-3.5 py-2.5 flex flex-col items-center border-r border-border/40">
              <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Remaining</span>
              <span className="text-foreground text-sm font-black mt-0.5">{distKm} <span className="text-[10px] font-semibold text-muted-foreground">km</span></span>
            </div>
            <div className="px-3.5 py-2.5 flex flex-col items-center">
              <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Cold-Chain</span>
              <span className="text-emerald-600 dark:text-emerald-400 text-sm font-black mt-0.5">3.8°C <span className="text-[10px] font-semibold text-emerald-600/70">OK</span></span>
            </div>
          </div>

          <div className="absolute top-3 right-3 z-[999] flex flex-col gap-2">
            <button
              onClick={recenter}
              className="bg-white/95 dark:bg-zinc-900/95 backdrop-blur-sm text-foreground px-3 py-2 rounded-xl shadow-lg border border-border/60 hover:bg-muted transition-all text-[11px] font-bold flex items-center gap-1.5"
            >
              🎯 Center
            </button>
            <button
              onClick={fitAll}
              className="bg-white/95 dark:bg-zinc-900/95 backdrop-blur-sm text-foreground px-3 py-2 rounded-xl shadow-lg border border-border/60 hover:bg-muted transition-all text-[11px] font-bold flex items-center gap-1.5"
            >
              🗺 Full Route
            </button>
            <button
              onClick={restartSimulation}
              className="bg-primary text-primary-foreground px-3 py-2 rounded-xl shadow-lg border border-primary/80 hover:opacity-90 transition-all text-[11px] font-bold flex items-center gap-1.5"
            >
              ↺ Replay Flow
            </button>
          </div>

          <div className="absolute bottom-9 left-3 z-[999] bg-black/60 backdrop-blur-sm text-white text-[10px] px-2.5 py-1 rounded-full font-semibold flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse inline-block" />
            {ping}
          </div>
        </div>

        <div className="px-5 py-3.5 border-t border-border/60 bg-muted/30">
          <div className="flex justify-between items-center text-xs mb-2">
            <span className="font-semibold text-muted-foreground flex items-center gap-1.5">
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-blue-500 border-2 border-white shadow" />
              Blood Reserve
            </span>
            <span className="font-extrabold text-foreground tabular-nums">{progress}%</span>
            <span className="font-semibold text-muted-foreground flex items-center gap-1.5">
              {hospitalName || 'Hospital'}
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-red-500 border-2 border-white shadow" />
            </span>
          </div>
          <div className="relative h-2.5 w-full bg-muted rounded-full overflow-hidden">
            <div
              className={`absolute inset-y-0 left-0 transition-all duration-700 rounded-full ${
                phase === 'DELIVERED' ? 'bg-emerald-500' : 'bg-gradient-to-r from-emerald-500 to-red-500'
              }`}
              style={{ width: `${Math.max(progress, 2)}%` }}
            />
          </div>
        </div>

        <div className="px-5 py-4 bg-card">
          <div className="flex flex-col md:flex-row md:items-center gap-5">
            <div className="flex items-center gap-3.5 flex-shrink-0">
              <div className="relative">
                <div className="w-14 h-14 rounded-full bg-gradient-to-br from-red-500 to-rose-700 flex items-center justify-center text-white font-black text-lg shadow-lg border-2 border-white dark:border-zinc-800 select-none">
                  RP
                </div>
                <span className="absolute -bottom-0.5 -right-0.5 bg-emerald-500 text-white text-[10px] rounded-full w-5 h-5 flex items-center justify-center border-2 border-white dark:border-zinc-800 shadow font-bold">✓</span>
              </div>
              <div>
                <div className="font-extrabold text-sm text-foreground flex items-center gap-1.5">
                  Rajesh Patil
                  <span className="text-amber-500 text-xs font-bold">★ 4.9</span>
                </div>
                <p className="text-xs text-muted-foreground">Certified Trauma Dispatch Pilot</p>
                <p className="text-[11px] font-mono font-bold text-primary mt-0.5">MH-02-ER-9014 · ICU Ambulance</p>
              </div>
            </div>

            <div className="flex-1 grid grid-cols-3 gap-2.5 text-xs">
              {[
                { label: 'Consignment', value: `${bloodType || 'O-'} · ${units || 2} Units`, color: 'text-red-600 dark:text-red-400' },
                { label: 'Cold-Chain', value: 'Active (2°C–6°C)', color: 'text-emerald-600 dark:text-emerald-400' },
                { label: 'Protocol', value: 'Green Corridor', color: 'text-foreground' },
              ].map(({ label, value, color }) => (
                <div key={label} className="bg-muted/50 border border-border/50 rounded-xl px-3 py-2.5 space-y-0.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground block">{label}</span>
                  <span className={`font-extrabold text-[11px] ${color}`}>{value}</span>
                </div>
              ))}
            </div>

            <div className="flex flex-col sm:flex-row md:flex-col gap-2 flex-shrink-0">
              <a
                href="tel:108"
                className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-primary text-primary-foreground text-xs font-extrabold shadow-md hover:opacity-90 active:scale-95 transition-all whitespace-nowrap"
              >
                📞 Call Pilot
              </a>
              <a
                href="tel:112"
                className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-destructive/10 text-destructive border border-destructive/30 text-xs font-extrabold shadow-sm hover:bg-destructive/20 active:scale-95 transition-all whitespace-nowrap"
              >
                🚨 Police SOS
              </a>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// MAIN HOSPITAL EMERGENCY TRACKING PAGE
// ══════════════════════════════════════════════════════════════════════════════
export default function HospitalEmergencyTrackingPage() {
  const params = useParams();
  const requestId = params?.id as string;

  const [request, setRequest] = useState<EmergencyRequestData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());

  const [liveStatus, setLiveStatus] = useState<string>('PENDING');
  const [fulfilledUnits, setFulfilledUnits] = useState<number>(0);

  const fetchRequest = useCallback(async () => {
    if (!requestId) return;
    try {
      const res = await emergencyService.getRequest(requestId);
      if (res.success && res.data) {
        setRequest(res.data);
        setLiveStatus(res.data.status || 'PENDING');
        setFulfilledUnits(res.data.units_fulfilled || 0);
        setError(null);
        setLastRefreshed(new Date());
      } else {
        // Fallback for demo ID
        setRequest({
          id: requestId,
          request_number: requestId,
          blood_type: 'O-',
          units_required: 2,
          units_fulfilled: 0,
          urgency_level: 'CRITICAL',
          status: 'IN_TRANSIT',
          city: 'Mumbai',
          hospital_name: 'Lilavati Hospital & Research Centre',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          ai_assisted: true,
          latitude: 19.0518,
          longitude: 72.8290,
        } as any);
      }
    } catch (err: any) {
      setRequest({
        id: requestId,
        request_number: requestId,
        blood_type: 'O-',
        units_required: 2,
        units_fulfilled: 0,
        urgency_level: 'CRITICAL',
        status: 'IN_TRANSIT',
        city: 'Mumbai',
        hospital_name: 'Lilavati Hospital & Research Centre',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        ai_assisted: true,
        latitude: 19.0518,
        longitude: 72.8290,
      } as any);
    } finally {
      setLoading(false);
    }
  }, [requestId]);

  useEffect(() => {
    fetchRequest();
    const id = setInterval(fetchRequest, 8000);
    return () => clearInterval(id);
  }, [fetchRequest]);

  const handleStatusChange = useCallback((newStatus: string, unitsDone: number) => {
    setLiveStatus(newStatus);
    setFulfilledUnits(unitsDone);
  }, []);

  const statusVariant = (s: string) =>
    s === 'FULFILLED' ? 'success' : s === 'CANCELLED' ? 'outline' : s === 'IN_TRANSIT' || s === 'DISPATCHED' ? 'default' : 'critical';

  const stageActive = (s: string, stages: string[]) => stages.includes(s);

  return (
    <div className="min-h-screen pb-16">
      <div className="container mx-auto max-w-4xl px-4 sm:px-6 pt-10 sm:pt-14 space-y-8">

        {/* ── Breadcrumb & Page Header ── */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-border/60 pb-5">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground mb-1">
              <Link href="/hospital" className="hover:text-primary transition-colors">
                Hospital Console
              </Link>
              <span>/</span>
              <Link href="/hospital/emergency" className="hover:text-primary transition-colors">
                Emergency Command Desk
              </Link>
              <span>/</span>
              <span className="text-foreground font-mono">{request?.request_number || requestId}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
              Hospital Live Dispatch Tracker
            </h1>
            {request && (
              <p className="text-xs text-muted-foreground mt-1">
                Clinical Requisition #{request.request_number} &bull; Destination: <strong>{request.hospital_name || 'Lilavati Hospital'}</strong> &bull; Refreshed {lastRefreshed.toLocaleTimeString()}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Link href="/hospital/emergency">
              <Button variant="outline" size="sm" className="text-xs">
                &larr; Emergency Desk
              </Button>
            </Link>
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchRequest()}
              isLoading={loading}
              className="text-xs"
            >
              ↺ Refresh
            </Button>
          </div>
        </div>

        {/* ── Error ── */}
        {error && (
          <div className="rounded-2xl border border-destructive/40 bg-destructive/8 p-6 text-center space-y-3">
            <div className="text-2xl">⚠️</div>
            <p className="text-sm font-bold text-destructive">{error}</p>
            <Link href="/hospital/emergency">
              <Button variant="danger" size="sm">Back to Hospital Emergency Desk</Button>
            </Link>
          </div>
        )}

        {/* ── Skeleton ── */}
        {loading && !request && (
          <div className="py-20 flex flex-col items-center gap-4">
            <span className="h-10 w-10 rounded-full border-2 border-primary border-t-transparent animate-spin" />
            <span className="text-sm text-muted-foreground animate-pulse">Connecting to LifeLink Emergency Corridor…</span>
          </div>
        )}

        {/* ── Request Loaded ── */}
        {request && (
          <>
            {/* Requisition Overview Card */}
            <Card className="border-border/60 shadow-md bg-card">
              <CardHeader className="border-b border-border/60 pb-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">🚨</span>
                      <h2 className="text-2xl font-black font-mono tracking-tight text-foreground">
                        {request.request_number}
                      </h2>
                    </div>
                    <p className="text-[11px] text-muted-foreground mt-0.5">
                      Hospital Facility Requisition &bull; Clinical Transfusion Protocol Active
                    </p>
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant={statusVariant(liveStatus)} className="font-extrabold uppercase tracking-wide">
                      {liveStatus.replace('_', ' ')}
                    </Badge>
                    <Badge variant="default">{request.urgency_level}</Badge>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="pt-5">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    { label: 'Blood Group', value: request.blood_type, cls: 'text-primary' },
                    { label: 'Units Required', value: String(request.units_required), cls: 'text-foreground' },
                    { label: 'Units Fulfilled', value: String(fulfilledUnits), cls: fulfilledUnits > 0 ? 'text-emerald-600 dark:text-emerald-400 font-extrabold' : 'text-muted-foreground' },
                    { label: 'City', value: request.city || 'Mumbai', cls: 'text-foreground text-xl' },
                  ].map(({ label, value, cls }) => (
                    <div key={label} className="p-3.5 rounded-2xl bg-muted/50 border border-border/50 text-center">
                      <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider block mb-1">{label}</span>
                      <span className={`text-2xl font-black ${cls}`}>{value}</span>
                    </div>
                  ))}
                </div>

                <div className="mt-5 border-t border-border/50 pt-4 grid sm:grid-cols-3 gap-3 text-xs">
                  <div>
                    <span className="text-muted-foreground block mb-0.5">Destination Facility</span>
                    <strong className="text-foreground">{request.hospital_name || 'Lilavati Hospital & Research Centre'}</strong>
                  </div>
                  <div>
                    <span className="text-muted-foreground block mb-0.5">Requisition Time</span>
                    <span className="text-foreground font-mono">{new Date(request.created_at).toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block mb-0.5">Corridor Level</span>
                    <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Priority 1 Traffic Signal Override</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ── LIVE TRACKING MAP ── */}
            <LiveTracker
              requestId={requestId}
              hospitalName={request.hospital_name || 'Lilavati Hospital & Research Centre'}
              hospitalLat={request.latitude || 19.0518}
              hospitalLng={request.longitude || 72.829}
              bloodType={request.blood_type}
              units={request.units_required}
              requestStatus={liveStatus}
              onStatusChange={handleStatusChange}
            />

            {/* ── Lifecycle Stepper ── */}
            <Card className="border-border/60 shadow-md bg-card">
              <CardHeader className="pb-2">
                <CardTitle className="text-base font-extrabold">Requisition Lifecycle</CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">Real-time operational stages updated automatically upon delivery.</p>
              </CardHeader>
              <CardContent className="pt-4">
                {liveStatus === 'CANCELLED' ? (
                  <div className="p-4 rounded-2xl border border-muted bg-muted/40 text-center">
                    <span className="text-xs font-bold text-muted-foreground uppercase">Requisition Cancelled</span>
                    <p className="text-sm text-muted-foreground mt-1">This requisition has been marked as cancelled.</p>
                  </div>
                ) : (
                  <ol className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                    {[
                      {
                        step: 1,
                        label: 'Hospital Requisition Raised',
                        sub: 'Clinical Intake Logged',
                        desc: 'Requisition recorded under hospital facility code.',
                        active: true,
                        color: 'primary',
                      },
                      {
                        step: 2,
                        label: 'Matching & Coordination',
                        sub: 'Compatible Discovery',
                        desc: 'Inventory search & cold-box allocation at Kurla Reserve.',
                        active: stageActive(liveStatus, ['MATCHING', 'DISPATCHED', 'IN_TRANSIT', 'FULFILLED']),
                        color: 'primary',
                      },
                      {
                        step: 3,
                        label: 'Dispatch / In Transit',
                        sub: 'Green Corridor Pilot',
                        desc: 'ICU Ambulance in transit with thermal consignment.',
                        active: stageActive(liveStatus, ['DISPATCHED', 'IN_TRANSIT', 'FULFILLED']),
                        color: 'primary',
                      },
                      {
                        step: 4,
                        label: 'Fulfilled & Handover',
                        sub: 'Units Delivered',
                        desc: 'Blood units received & verified by Hospital ICU team.',
                        active: liveStatus === 'FULFILLED',
                        color: 'green',
                      },
                    ].map(({ step, label, sub, desc, active, color }) => (
                      <li
                        key={step}
                        className={`p-4 rounded-2xl border space-y-1 transition-all ${
                          active
                            ? color === 'green' && liveStatus === 'FULFILLED'
                              ? 'border-emerald-500/60 bg-emerald-500/15 shadow-md'
                              : 'border-primary/40 bg-primary/10'
                            : 'border-border/50 bg-muted/30 opacity-70'
                        }`}
                      >
                        <span className={`text-[10px] font-extrabold uppercase tracking-wider block ${
                          active
                            ? color === 'green' && liveStatus === 'FULFILLED'
                              ? 'text-emerald-600 dark:text-emerald-400'
                              : 'text-primary'
                            : 'text-muted-foreground'
                        }`}>{step}. {label}</span>
                        <h3 className="font-bold text-sm text-foreground">{sub}</h3>
                        <p className="text-[11px] text-muted-foreground leading-relaxed">{desc}</p>
                        {active && (
                          <span className={`inline-block mt-1 text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            color === 'green' && liveStatus === 'FULFILLED'
                              ? 'bg-emerald-500 text-white shadow-sm'
                              : 'bg-primary/15 text-primary'
                          }`}>
                            {step === 4 && liveStatus === 'FULFILLED' ? '✓ Complete & Handed Over' : '● Active'}
                          </span>
                        )}
                      </li>
                    ))}
                  </ol>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}
