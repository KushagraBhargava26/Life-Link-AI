'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { emergencyService } from '@/services/emergencyService';
import type { EmergencyRequestData } from '@/types';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

const statusLabels: Record<string, string> = {
  PENDING: 'Pending review',
  MATCHING: 'Matching in progress',
  NOTIFIED: 'Facilities notified',
  CONFIRMED: 'Support confirmed',
  IN_PROGRESS: 'In progress',
  PARTIALLY_FULFILLED: 'Partially fulfilled',
  FULFILLED: 'Fulfilled',
  CANCELLED: 'Cancelled',
  EXPIRED: 'Expired',
};

function statusVariant(status: string): 'critical' | 'warning' | 'success' | 'outline' | 'info' {
  if (status === 'FULFILLED') return 'success';
  if (status === 'CANCELLED' || status === 'EXPIRED') return 'outline';
  if (status === 'PENDING' || status === 'MATCHING') return 'warning';
  if (status === 'PARTIALLY_FULFILLED') return 'info';
  return 'critical';
}

function formatDate(value?: string | null) {
  if (!value) return 'Not available';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Not available' : date.toLocaleString();
}

export function RequestTrackingView({ requestId, isPublic = false }: { requestId: string; isPublic?: boolean }) {
  const [request, setRequest] = useState<EmergencyRequestData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastCheckedAt, setLastCheckedAt] = useState<Date | null>(null);
  const [vehicleLocation, setVehicleLocation] = useState<{
    latitude: number;
    longitude: number;
    heading?: number;
    speed_kmh?: number;
    status_note?: string;
    recorded_at: string;
  } | null>(null);

  const fetchRequest = useCallback(async (manual = false) => {
    if (!requestId) return;
    if (manual) setRefreshing(true);
    try {
      const response = await emergencyService.getRequest(requestId);
      if (!response.success || !response.data) {
        throw new Error(response.message || 'Request details could not be loaded.');
      }
      setRequest(response.data);
      setError(null);
      setLastCheckedAt(new Date());

      // Fetch latest vehicle GPS tracking telemetry
      try {
        const locRes = await emergencyService.getLocation(requestId);
        if (locRes?.success && locRes.data) {
          setVehicleLocation(locRes.data);
        }
      } catch {
        // GPS data optional, ignore 404/silence
      }
    } catch (cause: any) {
      setError(cause.response?.data?.error?.message || cause.message || 'Could not connect to the request service.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [requestId]);

  useEffect(() => {
    void fetchRequest();
    const intervalId = window.setInterval(() => void fetchRequest(), 8000);
    return () => window.clearInterval(intervalId);
  }, [fetchRequest]);

  const status = request?.status?.toUpperCase() || '';
  const label = statusLabels[status] || status.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase());
  const backHref = isPublic ? '/emergency' : '/hospital/emergency';

  return (
    <section className="mx-auto w-full max-w-4xl space-y-6 px-4 py-6 sm:px-6 sm:py-9" aria-labelledby="tracking-title">
      <header className="flex flex-col gap-4 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <Link href={backHref} className="inline-flex min-h-11 items-center text-sm font-medium text-primary hover:underline">
            {isPublic ? 'Back to emergency intake' : 'Back to emergency desk'}
          </Link>
          <h1 id="tracking-title" className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">Request status</h1>
          <p className="mt-1 break-words text-sm text-muted-foreground">{request ? `Request ${request.request_number}` : `Request ${requestId}`}</p>
        </div>
        <Button type="button" variant="outline" size="md" onClick={() => void fetchRequest(true)} isLoading={refreshing}>
          Refresh status
        </Button>
      </header>

      {error && (
        <div role="alert" className="rounded-lg border border-critical/30 bg-critical-subtle p-4 text-sm text-critical">
          <p className="font-semibold">{request ? 'Could not refresh this request' : 'Request details are unavailable'}</p>
          <p className="mt-1">{error}</p>
          <Button type="button" variant="outline" size="sm" className="mt-3" onClick={() => void fetchRequest(true)} isLoading={refreshing}>Try again</Button>
        </div>
      )}

      {loading && !request ? (
        <Card aria-live="polite"><CardContent className="flex min-h-40 items-center justify-center text-sm text-muted-foreground">Loading request details…</CardContent></Card>
      ) : request ? (
        <>
          <Card className="border-l-4 border-l-primary">
            <CardHeader className="mb-3 flex-row flex-wrap items-center justify-between gap-3">
              <div>
                <CardTitle className="text-base">Current request status</CardTitle>
                <p className="mt-1 text-sm text-muted-foreground">Status supplied by the request service.</p>
              </div>
              <span aria-live="polite"><Badge variant={statusVariant(status)} size="lg">{label || 'Status unavailable'}</Badge></span>
            </CardHeader>
            <CardContent className="grid grid-cols-1 gap-4 border-t border-border pt-4 sm:grid-cols-2 lg:grid-cols-3">
              <div><p className="text-xs font-medium text-muted-foreground">Blood group</p><p className="mt-1 text-lg font-semibold">{request.blood_type || 'Not available'}</p></div>
              <div><p className="text-xs font-medium text-muted-foreground">Units requested</p><p className="mt-1 text-lg font-semibold">{request.units_required}</p></div>
              <div><p className="text-xs font-medium text-muted-foreground">Units fulfilled</p><p className="mt-1 text-lg font-semibold">{request.units_fulfilled}</p></div>
              <div><p className="text-xs font-medium text-muted-foreground">Urgency</p><p className="mt-1 text-sm font-semibold">{request.urgency_level || 'Not available'}</p></div>
              <div><p className="text-xs font-medium text-muted-foreground">Facility</p><p className="mt-1 break-words text-sm font-semibold">{request.hospital_name || 'Not listed'}</p></div>
              <div><p className="text-xs font-medium text-muted-foreground">City</p><p className="mt-1 text-sm font-semibold">{request.city || 'Not listed'}</p></div>
              <div><p className="text-xs font-medium text-muted-foreground">Request created</p><p className="mt-1 text-sm">{formatDate(request.created_at)}</p></div>
              <div><p className="text-xs font-medium text-muted-foreground">Last updated</p><p className="mt-1 text-sm">{formatDate(request.updated_at)}</p></div>
              {!isPublic && request.facility_address && <div className="sm:col-span-2 lg:col-span-3"><p className="text-xs font-medium text-muted-foreground">Facility address</p><p className="mt-1 break-words text-sm">{request.facility_address}</p></div>}
            </CardContent>
          </Card>

          {/* Live Vehicle / Dispatch Location Tracking Card */}
          {vehicleLocation && (
            <Card className="border-l-4 border-l-success">
              <CardHeader className="mb-2 flex-row flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75" />
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-success" />
                  </span>
                  <CardTitle className="text-base">Live Dispatch & Location Tracking</CardTitle>
                </div>
                <Badge variant="success" size="sm">Active Telemetry</Badge>
              </CardHeader>
              <CardContent className="space-y-3 border-t border-border pt-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">Coordinates</p>
                    <p className="mt-1 font-mono text-sm font-semibold">
                      {vehicleLocation.latitude.toFixed(5)}, {vehicleLocation.longitude.toFixed(5)}
                    </p>
                  </div>
                  {vehicleLocation.speed_kmh !== null && vehicleLocation.speed_kmh !== undefined && (
                    <div>
                      <p className="text-xs font-medium text-muted-foreground">Speed</p>
                      <p className="mt-1 text-sm font-semibold">{vehicleLocation.speed_kmh} km/h</p>
                    </div>
                  )}
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">Telemetry Recorded</p>
                    <p className="mt-1 text-sm font-semibold">{formatDate(vehicleLocation.recorded_at)}</p>
                  </div>
                </div>
                {vehicleLocation.status_note && (
                  <div className="rounded-lg bg-muted/40 p-3 text-xs text-foreground">
                    <span className="font-semibold text-muted-foreground">Status Note: </span>
                    {vehicleLocation.status_note}
                  </div>
                )}
                <div className="pt-1">
                  <a
                    href={`https://www.openstreetmap.org/?mlat=${vehicleLocation.latitude}&mlon=${vehicleLocation.longitude}#map=16/${vehicleLocation.latitude}/${vehicleLocation.longitude}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs font-medium text-primary hover:underline"
                  >
                    📍 View Dispatch on OpenStreetMap &rarr;
                  </a>
                </div>
              </CardContent>
            </Card>
          )}

          <p className="text-xs text-muted-foreground">
            {lastCheckedAt ? `Checked ${lastCheckedAt.toLocaleTimeString()}. Status refreshes about every 8 seconds while this page is open.` : 'Status refreshes about every 8 seconds while this page is open.'}
          </p>
        </>
      ) : !loading && !error ? (
        <Card><CardContent className="py-10 text-center text-sm text-muted-foreground">No request details were returned.</CardContent></Card>
      ) : null}
    </section>
  );
}
