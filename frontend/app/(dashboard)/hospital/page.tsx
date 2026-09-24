'use client';

// frontend/app/(dashboard)/hospital/page.tsx
// LifeLink AI — Hospital Operations Dashboard
// Architecture Reference: ARCHITECTURE.md Section 15, 27; DATABASE.md Section 7

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { hospitalService } from '@/services/hospitalService';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import type { HospitalDashboardData } from '@/types';

export default function HospitalDashboardPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [dashboard, setDashboard] = useState<HospitalDashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New Request Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [reqForm, setReqForm] = useState({
    blood_type: 'O-',
    units_required: 2,
    urgency_level: 'CRITICAL',
    patient_name: '',
    patient_age: '',
    notes: '',
  });

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await hospitalService.getDashboard();
      setDashboard(data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        router.push('/hospital/profile');
        return;
      }
      setError(err.response?.data?.error?.message || 'Failed to load hospital operational data.');
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated, loadData]);

  const handleCreateRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    if (!reqForm.blood_type) {
      setError('Blood group is required.');
      setIsSubmitting(false);
      return;
    }

    if (reqForm.patient_name.trim() && /\d/.test(reqForm.patient_name)) {
      setError('Patient identifier/name cannot contain numbers.');
      setIsSubmitting(false);
      return;
    }

    try {
      const payload: any = {
        blood_type: reqForm.blood_type,
        units_required: Number(reqForm.units_required),
        urgency_level: reqForm.urgency_level,
        notes: reqForm.notes.trim() || undefined,
      };
      if (reqForm.patient_name.trim()) {
        payload.patient_name = reqForm.patient_name.trim();
      }
      if (reqForm.patient_age) {
        payload.patient_age = Number(reqForm.patient_age);
      }

      const res = await hospitalService.createEmergencyRequest(payload);
      setSubmitSuccess(`Emergency Requisition ${res.request_number} created! Redirecting to Live Dispatch Tracker...`);
      setTimeout(() => {
        setModalOpen(false);
        setSubmitSuccess(null);
        router.push(`/emergency/track/${res.request_number}`);
      }, 1200);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to create emergency requisition.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="flex flex-col items-center gap-3 text-muted-foreground">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm font-medium">Connecting to Hospital Operations Console...</p>
        </div>
      </div>
    );
  }

  const hospital = dashboard?.hospital;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              {hospital?.name || 'Hospital Facility Operations'}
            </h1>
            {hospital?.is_verified ? (
              <Badge variant="success" size="sm">✓ Verified Facility</Badge>
            ) : (
              <Badge variant="warning" size="sm">Verification Pending (Admin Review)</Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground">
            {hospital?.city}, {hospital?.state} &bull; Type: <span className="font-semibold">{hospital?.type}</span>
            {hospital?.registration_number && ` &bull; Reg: ${hospital.registration_number}`}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link href="/hospital/profile">
            <Button variant="outline" size="sm">
              ⚙️ Facility Profile
            </Button>
          </Link>
          <Button
            variant="danger"
            size="sm"
            onClick={() => setModalOpen(true)}
            className="shadow-sm font-bold"
          >
            + Create Blood Request
          </Button>
        </div>
      </div>

      {/* Verification Notice Banner if Pending */}
      {!hospital?.is_verified && (
        <div className="p-4 rounded-xl border border-warning/40 bg-warning/10 text-xs text-foreground flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-base">⏳</span>
            <span>
              <strong>Facility Verification Pending:</strong> Your hospital profile is awaiting administrative review. You can create emergency requisitions, but partner blood banks see your pending verification status.
            </span>
          </div>
          <Link href="/hospital/profile" className="font-semibold text-primary underline shrink-0 ml-4">
            Review Profile
          </Link>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl border border-critical/30 bg-critical-subtle text-critical text-sm">
          {error}
        </div>
      )}

      {/* Operational Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-semibold uppercase tracking-wider">
              Active Requisitions
            </CardDescription>
            <CardTitle className="text-3xl font-extrabold text-critical">
              {dashboard?.active_requests_count ?? 0}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            Emergency requests currently matching or in progress
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-semibold uppercase tracking-wider">
              Pending Requisitions
            </CardDescription>
            <CardTitle className="text-3xl font-extrabold text-warning">
              {dashboard?.pending_requests_count ?? 0}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            Awaiting blood bank or donor coordination
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-semibold uppercase tracking-wider">
              Registered Bed Count
            </CardDescription>
            <CardTitle className="text-3xl font-extrabold text-foreground">
              {hospital?.bed_count || 'N/A'}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            Inpatient critical care capacity
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-semibold uppercase tracking-wider">
              In-House Blood Bank
            </CardDescription>
            <CardTitle className="text-xl font-bold text-foreground">
              {hospital?.has_blood_bank ? (
                <span className="text-success flex items-center gap-1">✓ In-House Unit</span>
              ) : (
                <span className="text-muted-foreground">Network Linked</span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {hospital?.has_blood_bank
              ? 'On-premise storage and cross-match unit'
              : 'Relying on regional blood bank dispatches'}
          </CardContent>
        </Card>
      </div>

      {/* Active Emergency Requests Table */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-foreground">Active Clinical Requisitions</h2>
            <p className="text-xs text-muted-foreground">
              Real-time emergency tracking for {hospital?.name}
            </p>
          </div>
          <Link href="/hospital/requests">
            <Button variant="ghost" size="sm" className="text-xs">
              View All Requisitions &rarr;
            </Button>
          </Link>
        </div>

        {dashboard?.recent_requests && dashboard.recent_requests.length > 0 ? (
          <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-border bg-muted/40 text-xs font-semibold text-muted-foreground uppercase">
                  <tr>
                    <th className="px-4 py-3">Requisition ID</th>
                    <th className="px-4 py-3">Blood Type</th>
                    <th className="px-4 py-3">Units Needed</th>
                    <th className="px-4 py-3">Urgency</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Created</th>
                    <th className="px-4 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {dashboard.recent_requests.map((r) => (
                    <tr key={r.id} className="hover:bg-muted/20 transition-colors">
                      <td className="px-4 py-3 font-mono font-bold text-foreground">
                        {r.request_number}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant="critical" size="sm" className="font-mono">
                          {r.blood_type}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 font-semibold text-foreground">
                        {r.units_required} {r.units_required === 1 ? 'Unit' : 'Units'}
                      </td>
                      <td className="px-4 py-3">
                        <Badge
                          variant={
                            r.urgency_level === 'CRITICAL'
                              ? 'critical'
                              : r.urgency_level === 'HIGH'
                              ? 'warning'
                              : 'info'
                          }
                          size="sm"
                        >
                          {r.urgency_level}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant="default" size="sm">
                          {r.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-xs text-muted-foreground">
                        {r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Just now'}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Link href={`/emergency/track/${r.request_number}`}>
                            <Button variant="danger" size="sm" className="text-xs h-7 px-2.5 font-bold shadow-sm flex items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping" />
                              🚑 Live GPS Track
                            </Button>
                          </Link>
                          <Link href={`/hospital/requests/${r.id}/matches`}>
                            <Button variant="outline" size="sm" className="text-xs h-7 px-2 font-semibold">
                              Matches &rarr;
                            </Button>
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <Card className="border-dashed">
            <CardContent className="py-12 text-center flex flex-col items-center justify-center gap-3">
              <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center text-2xl">
                📋
              </div>
              <div className="max-w-md">
                <h3 className="text-base font-semibold text-foreground">
                  No emergency requisitions yet.
                </h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Create a request when your hospital needs blood.
                </p>
              </div>
              <Button
                variant="danger"
                size="sm"
                onClick={() => setModalOpen(true)}
                className="mt-2 font-bold"
              >
                + Create Blood Request
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Create Emergency Requisition Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Create Hospital Emergency Requisition"
      >
        <form onSubmit={handleCreateRequest} className="space-y-4">
          <p className="text-xs text-muted-foreground">
            This requisition will be created directly on behalf of <strong className="text-foreground">{hospital?.name}</strong>.
          </p>

          <div className="text-[11px] text-muted-foreground">
            <span className="text-destructive font-bold">*</span> Required field
          </div>

          {submitSuccess && (
            <div className="p-3 rounded-lg border border-success/30 bg-success-subtle text-success text-xs font-semibold">
              {submitSuccess}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">
                Blood Group Needed <span className="text-destructive">*</span>
              </label>
              <select
                value={reqForm.blood_type}
                onChange={(e) => setReqForm({ ...reqForm, blood_type: e.target.value })}
                className="w-full h-10 px-3 rounded-lg border border-border bg-background text-foreground text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-primary"
                required
              >
                {['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'].map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">
                Units Required (1-20) <span className="text-destructive">*</span>
              </label>
              <Input
                type="number"
                min="1"
                max="20"
                value={reqForm.units_required}
                onChange={(e) => setReqForm({ ...reqForm, units_required: Number(e.target.value) })}
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-foreground">
              Clinical Urgency <span className="text-destructive">*</span>
            </label>
            <select
              value={reqForm.urgency_level}
              onChange={(e) => setReqForm({ ...reqForm, urgency_level: e.target.value })}
              className="w-full h-10 px-3 rounded-lg border border-border bg-background text-foreground text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-primary"
              required
            >
              <option value="CRITICAL">CRITICAL — Imminent mortality (&lt; 30 min)</option>
              <option value="HIGH">HIGH — Severe blood loss (&lt; 2 hrs)</option>
              <option value="MEDIUM">MEDIUM — Scheduled surgery / stable</option>
              <option value="LOW">LOW — Routine buffer replenishment</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Patient Identifier (Optional)</label>
              <Input
                placeholder="e.g. Ward 4 / Trauma Case 12"
                value={reqForm.patient_name}
                onChange={(e) => setReqForm({ ...reqForm, patient_name: e.target.value })}
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Patient Age (Optional)</label>
              <Input
                type="number"
                min="1"
                max="120"
                placeholder="e.g. 45"
                value={reqForm.patient_age}
                onChange={(e) => setReqForm({ ...reqForm, patient_age: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-foreground">Clinical Transfusion Notes (Optional)</label>
            <textarea
              rows={2}
              placeholder="e.g. Multi-trauma accident, cross-match tube sent to lab"
              value={reqForm.notes}
              onChange={(e) => setReqForm({ ...reqForm, notes: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground text-xs focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-border">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="danger"
              size="sm"
              isLoading={isSubmitting}
              className="font-bold"
            >
              Create Requisition
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
