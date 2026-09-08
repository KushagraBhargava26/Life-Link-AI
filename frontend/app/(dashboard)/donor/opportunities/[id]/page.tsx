'use client';

// frontend/app/(dashboard)/donor/opportunities/[id]/page.tsx
// LifeLink AI — Donor Emergency Requisition Review & Response Workspace
// Architecture Reference: ARCHITECTURE.md Section 33 & Section 35

import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { donorService } from '@/services/donorService';
import { DonorOpportunityDetail } from '@/types';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

export default function DonorOpportunityDetailPage() {
  const params = useParams();
  const router = useRouter();
  const requestId = params?.id as string;

  const [opportunity, setOpportunity] = useState<DonorOpportunityDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [notes, setNotes] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchOpportunity = useCallback(async () => {
    if (!requestId) return;
    setLoading(true);
    setErrorMessage(null);
    try {
      const resp = await donorService.getOpportunity(requestId);
      if (resp.success && resp.data) {
        setOpportunity(resp.data);
        if (resp.data.donor_response?.notes) {
          setNotes(resp.data.donor_response.notes);
        }
      } else {
        setErrorMessage('Could not find emergency request details.');
      }
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || 'Failed to load emergency details.';
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  }, [requestId]);

  useEffect(() => {
    fetchOpportunity();
  }, [fetchOpportunity]);

  const handleRespond = async (status: 'ACCEPTED' | 'DECLINED') => {
    if (!requestId) return;
    setSubmitting(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const resp = await donorService.respondToOpportunity(requestId, {
        status,
        notes: notes.trim() || undefined,
      });

      if (resp.success && resp.data) {
        setSuccessMessage(
          status === 'ACCEPTED'
            ? 'Thank you for responding to this emergency request! The hospital coordination desk has been notified.'
            : 'You have declined this emergency request. Your availability remains on standby.'
        );
        // Refresh opportunity details
        await fetchOpportunity();
      }
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || 'Failed to register emergency response.';
      setErrorMessage(msg);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        <p className="text-xs text-muted-foreground">Loading emergency request details...</p>
      </div>
    );
  }

  if (errorMessage && !opportunity) {
    return (
      <div className="max-w-2xl mx-auto py-12 space-y-4">
        <div className="rounded-lg border border-critical/40 bg-critical/10 p-4 text-xs font-semibold text-critical">
          {errorMessage}
        </div>
        <Link href="/donor">
          <Button variant="outline" size="sm">
            ← Back to Donor Dashboard
          </Button>
        </Link>
      </div>
    );
  }

  const existingResponse = opportunity?.donor_response;

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      {/* Header Breadcrumb */}
      <div className="flex items-center justify-between border-b border-border/80 pb-4">
        <Link
          href="/donor"
          className="text-xs font-semibold text-muted-foreground hover:text-foreground flex items-center gap-1.5 transition-colors"
        >
          <span>←</span>
          <span>Back to Donor Dashboard</span>
        </Link>
        <Badge variant="outline" className="font-mono text-xs">
          {opportunity?.request_number}
        </Badge>
      </div>

      {/* Notifications */}
      {errorMessage && (
        <div className="rounded-lg border border-critical/40 bg-critical/10 p-4 text-xs font-semibold text-critical" role="alert">
          {errorMessage}
        </div>
      )}
      {successMessage && (
        <div className="rounded-lg border border-green-500/40 bg-green-500/10 p-4 text-xs font-semibold text-green-700 dark:text-green-300" role="status">
          {successMessage}
        </div>
      )}

      {/* Confirmation State if already responded */}
      {existingResponse && (
        <Card className={`border-2 ${existingResponse.status === 'ACCEPTED' ? 'border-green-500/60 bg-green-500/5' : 'border-border bg-card'}`}>
          <CardHeader className="pb-3 border-b border-border/60">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xl">
                  {existingResponse.status === 'ACCEPTED' ? '✅' : '⏸️'}
                </span>
                <CardTitle className="text-base font-bold">
                  {existingResponse.status === 'ACCEPTED' ? 'Response Registered: Available to Donate' : 'Response Registered: Request Declined'}
                </CardTitle>
              </div>
              <Badge variant={existingResponse.status === 'ACCEPTED' ? 'success' : 'outline'}>
                {existingResponse.status}
              </Badge>
            </div>
            <CardDescription className="text-xs">
              Response recorded at {new Date(existingResponse.responded_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })} IST
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-4 text-xs space-y-3">
            {existingResponse.status === 'ACCEPTED' ? (
              <div className="space-y-2">
                <p className="text-foreground leading-relaxed">
                  Thank you for responding to this emergency request. Your compatibility and availability have been shared with the hospital coordination desk.
                </p>
                <div className="p-3 rounded-lg bg-background border border-border text-muted-foreground space-y-1 text-[11px]">
                  <strong className="text-foreground block">Next Steps:</strong>
                  <p>1. The hospital coordination team reviews incoming responses.</p>
                  <p>2. If shortlisted, attending staff will coordinate donation timing directly.</p>
                </div>
                {existingResponse.notes && (
                  <p className="text-muted-foreground text-[11px]">
                    <strong>Your Note:</strong> {existingResponse.notes}
                  </p>
                )}
              </div>
            ) : (
              <p className="text-muted-foreground leading-relaxed">
                You marked this request as declined. If your situation changes and you wish to accept, you can update your response below.
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Emergency Clinical Requisition Details */}
      <Card className="border-border bg-card shadow-sm">
        <CardHeader className="border-b border-border/60 pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-critical animate-pulse" />
              <Badge variant="critical">🚨 {opportunity?.urgency_level} Urgency</Badge>
            </div>
            <span className="text-xs text-muted-foreground font-medium">
              Status: <strong className="text-foreground capitalize">{opportunity?.status?.toLowerCase()}</strong>
            </span>
          </div>
          <CardTitle className="text-xl font-bold text-foreground mt-2">
            {opportunity?.hospital_name || 'Emergency Trauma Facility'}
          </CardTitle>
          <CardDescription className="text-xs">
            📍 {opportunity?.facility_address ? `${opportunity.facility_address}, ` : ''}{opportunity?.city}
          </CardDescription>
        </CardHeader>

        <CardContent className="pt-6 space-y-6">
          {/* Blood & Units Requirement Highlight */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl border border-critical/30 bg-critical/5 space-y-1">
              <span className="text-xs uppercase tracking-wider font-bold text-critical block">
                Required Blood Group
              </span>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-black text-critical">
                  🩸 {opportunity?.blood_type}
                </span>
                <span className="text-xs text-muted-foreground">
                  (Whole Blood)
                </span>
              </div>
              <p className="text-[11px] text-muted-foreground">
                Your Blood Group: <strong className="text-foreground">{opportunity?.donor_blood_type}</strong> (Compatible)
              </p>
            </div>

            <div className="p-4 rounded-xl border border-border bg-muted/40 space-y-1">
              <span className="text-xs uppercase tracking-wider font-bold text-muted-foreground block">
                Units Required
              </span>
              <div className="text-2xl font-black text-foreground">
                {opportunity?.units_requested} {opportunity?.units_requested === 1 ? 'Unit' : 'Units'}
              </div>
              <p className="text-[11px] text-muted-foreground">
                Fulfilled so far: {opportunity?.units_fulfilled || 0} units
              </p>
            </div>
          </div>

          {/* Response Form */}
          <div className="pt-4 border-t border-border/60 space-y-4">
            <div>
              <label htmlFor="response-notes" className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Optional Response Note / Estimated Arrival Time
              </label>
              <Input
                id="response-notes"
                placeholder="e.g. Can reach hospital in 25 minutes, available immediately"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                maxLength={500}
                className="text-xs"
              />
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
              <Button
                variant="danger"
                size="lg"
                onClick={() => handleRespond('ACCEPTED')}
                isLoading={submitting}
                className="w-full sm:w-2/3 font-bold shadow-md shadow-critical/20"
              >
                <span>🚨 {existingResponse?.status === 'ACCEPTED' ? 'Update Acceptance' : 'Respond & Accept Opportunity'}</span>
              </Button>

              <Button
                variant="outline"
                size="lg"
                onClick={() => handleRespond('DECLINED')}
                isLoading={submitting}
                className="w-full sm:w-1/3 text-xs"
              >
                <span>Decline Request</span>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
