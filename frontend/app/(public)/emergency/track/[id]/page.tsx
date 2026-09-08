'use client';

// frontend/app/(public)/emergency/track/[id]/page.tsx
// LifeLink AI — Truthful Emergency Requisition Tracking
// Architecture Reference: ARCHITECTURE.md Section 17 & Section 30

import React, { useEffect, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { emergencyService } from '@/services/emergencyService';
import { EmergencyRequestData } from '@/types';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';

export default function EmergencyTrackingPage() {
  const params = useParams();
  const requestId = params?.id as string;

  const [request, setRequest] = useState<EmergencyRequestData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());

  const fetchRequestDetails = useCallback(async () => {
    if (!requestId) return;
    try {
      const response = await emergencyService.getRequest(requestId);
      if (response.success && response.data) {
        setRequest(response.data);
        setError(null);
        setLastRefreshed(new Date());
      } else {
        setError(response.message || 'Emergency record not found.');
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Could not connect to emergency registry.');
    } finally {
      setLoading(false);
    }
  }, [requestId]);

  useEffect(() => {
    fetchRequestDetails();
    const interval = setInterval(fetchRequestDetails, 8000);
    return () => clearInterval(interval);
  }, [fetchRequestDetails]);

  return (
    <div className="py-10 sm:py-16">
      <div className="container mx-auto max-w-4xl px-4 sm:px-6 space-y-8">
        
        {/* Top Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-4">
          <div>
            <Link href="/emergency" className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1">
              ← Return to Emergency Intake
            </Link>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight mt-1 text-foreground">
              Emergency Requisition Tracker
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground hidden sm:inline">
              Refreshed: {lastRefreshed.toLocaleTimeString()}
            </span>
            <Button variant="outline" size="sm" onClick={() => fetchRequestDetails()} isLoading={loading} className="text-xs">
              Refresh
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="rounded-xl border border-critical/40 bg-critical/10 p-6 text-center space-y-3" role="alert">
            <p className="text-sm font-bold text-critical">{error}</p>
            <Link href="/emergency">
              <Button variant="danger" size="sm">
                Submit New Requisition
              </Button>
            </Link>
          </div>
        )}

        {/* Loading Skeleton */}
        {loading && !request && (
          <div className="py-16 flex flex-col items-center justify-center space-y-3">
            <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
            <span className="text-sm text-muted-foreground">Connecting to LifeLink Emergency Registry...</span>
          </div>
        )}

        {/* Tracking Details */}
        {request && (
          <>
            {/* Overview Card */}
            <Card className="border-border shadow-md bg-card">
              <CardHeader className="border-b border-border/60 pb-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-2xl" aria-hidden="true">🚨</span>
                      <h2 className="text-2xl font-black font-mono tracking-tight text-foreground">
                        {request.request_number}
                      </h2>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Verified Clinical Tracking Code • DPDP Privacy Shield Active
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge variant={request.status === 'FULFILLED' ? 'success' : request.status === 'CANCELLED' ? 'outline' : 'critical'}>
                      {request.status}
                    </Badge>
                    <Badge variant="default">
                      {request.urgency_level}
                    </Badge>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="pt-6">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                  <div className="p-3.5 rounded-xl bg-card-elevated border border-border">
                    <span className="text-xs text-muted-foreground block mb-1">Blood Group</span>
                    <span className="text-2xl font-black text-primary">{request.blood_type}</span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-card-elevated border border-border">
                    <span className="text-xs text-muted-foreground block mb-1">Units Required</span>
                    <span className="text-2xl font-black text-foreground">{request.units_required}</span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-card-elevated border border-border">
                    <span className="text-xs text-muted-foreground block mb-1">Units Fulfilled</span>
                    <span className="text-2xl font-black text-green-600 dark:text-green-400">{request.units_fulfilled}</span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-card-elevated border border-border">
                    <span className="text-xs text-muted-foreground block mb-1">City</span>
                    <span className="text-xl font-bold text-foreground truncate">{request.city}</span>
                  </div>
                </div>

                <div className="mt-6 space-y-2.5 border-t border-border/60 pt-4 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Destination Facility:</span>
                    <strong className="text-foreground">{request.hospital_name || 'Hospital Specified'}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Requisition Timestamp:</span>
                    <span className="text-foreground font-mono">{new Date(request.created_at).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Clinical Confidentiality:</span>
                    <span className="text-green-600 dark:text-green-400 font-semibold">DPDP Shield Active (Zero Patient PII Exposed)</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Truthful Requisition Stepper */}
            <Card className="border-border shadow-md bg-card">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Requisition Lifecycle</CardTitle>
                <CardDescription>Truthful operational stages recorded in PostgreSQL.</CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                {request.status === 'CANCELLED' ? (
                  <div className="p-4 rounded-xl border border-muted bg-muted/40 text-center space-y-1">
                    <span className="text-xs font-bold text-muted-foreground uppercase">Requisition Cancelled</span>
                    <p className="text-sm text-muted-foreground">This emergency requisition has been marked as cancelled in the database.</p>
                  </div>
                ) : (
                  <ol className="grid grid-cols-1 sm:grid-cols-4 gap-4" aria-label="Requisition Progress">
                    {/* Stage 1: Request Created */}
                    <li className="p-4 rounded-xl border border-primary/40 bg-primary/10 space-y-1">
                      <span className="text-xs font-bold text-primary block">1. Request Created</span>
                      <h3 className="font-bold text-sm text-foreground">Intake Logged</h3>
                      <p className="text-[11px] text-muted-foreground">Clinical requirements recorded in registry.</p>
                    </li>

                    {/* Stage 2: Matching & Coordination */}
                    <li
                      className={`p-4 rounded-xl border space-y-1 ${
                        ['MATCHING', 'MATCHED', 'NOTIFIED', 'DISPATCHED', 'IN_PROGRESS', 'FULFILLED', 'PARTIALLY_FULFILLED'].includes(request.status)
                          ? 'border-primary/40 bg-primary/10'
                          : 'border-border bg-card-elevated'
                      }`}
                    >
                      <span className="text-xs font-bold text-primary block">
                        2. Matching &amp; Coordination
                      </span>
                      <h3 className="font-bold text-sm text-foreground">Compatible Discovery</h3>
                      <p className="text-[11px] text-muted-foreground">Deterministic inventory and voluntary donor search.</p>
                    </li>

                    {/* Stage 3: Dispatched / In Progress */}
                    <li
                      className={`p-4 rounded-xl border space-y-1 ${
                        ['NOTIFIED', 'DISPATCHED', 'IN_PROGRESS', 'FULFILLED', 'PARTIALLY_FULFILLED'].includes(request.status)
                          ? 'border-primary/40 bg-primary/10'
                          : 'border-border bg-card-elevated'
                      }`}
                    >
                      <span className="text-xs font-bold text-primary block">
                        3. Dispatch / In Progress
                      </span>
                      <h3 className="font-bold text-sm text-foreground">Source Coordination</h3>
                      <p className="text-[11px] text-muted-foreground">Alerts communicated to matched blood banks or donors.</p>
                    </li>

                    {/* Stage 4: Fulfilled */}
                    <li
                      className={`p-4 rounded-xl border space-y-1 ${
                        request.status === 'FULFILLED'
                          ? 'border-green-500/40 bg-green-500/10'
                          : 'border-border bg-card-elevated'
                      }`}
                    >
                      <span className="text-xs font-bold text-green-600 dark:text-green-400 block">
                        4. Fulfilled
                      </span>
                      <h3 className="font-bold text-sm text-foreground">Units Delivered</h3>
                      <p className="text-[11px] text-muted-foreground">Blood units received and verified by facility.</p>
                    </li>
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
