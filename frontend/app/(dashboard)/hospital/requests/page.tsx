'use client';

// frontend/app/(dashboard)/hospital/requests/page.tsx
// LifeLink AI — Hospital Emergency Requisitions Management
// Architecture Reference: ARCHITECTURE.md Section 15, 27; API.md Section 8

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { hospitalService } from '@/services/hospitalService';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';

export default function HospitalRequestsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [requests, setRequests] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

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

  const loadRequests = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await hospitalService.getRequests({ limit: 50, offset: 0 });
      setRequests(data.items);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load emergency requisitions.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadRequests();
    }
  }, [isAuthenticated]);

  const handleCreateRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const payload: any = {
        blood_type: reqForm.blood_type,
        units_required: Number(reqForm.units_required),
        urgency_level: reqForm.urgency_level,
        notes: reqForm.notes || undefined,
      };
      if (reqForm.patient_name.trim()) {
        payload.patient_name = reqForm.patient_name.trim();
      }
      if (reqForm.patient_age) {
        payload.patient_age = Number(reqForm.patient_age);
      }

      const res = await hospitalService.createEmergencyRequest(payload);
      setSubmitSuccess(`Emergency Requisition ${res.request_number} dispatched! Redirecting to Live Dispatch Tracker...`);
      setTimeout(() => {
        setModalOpen(false);
        setSubmitSuccess(null);
        router.push(`/emergency/track/${res.request_number}`);
      }, 1200);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to create emergency request.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredRequests = requests.filter((r) => {
    if (statusFilter === 'ALL') return true;
    return r.status === statusFilter;
  });

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Hospital Requisitions Log
            </h1>
            <Badge variant="default" size="sm">{total} Total</Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            Complete audit and dispatch log of emergency blood requisitions for this facility.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link href="/hospital">
            <Button variant="outline" size="sm">
              &larr; Operations Console
            </Button>
          </Link>
          <Button
            variant="danger"
            size="sm"
            onClick={() => setModalOpen(true)}
            className="shadow-sm"
          >
            🚨 New Requisition
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-critical/30 bg-critical-subtle text-critical text-sm">
          {error}
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-border pb-3 text-xs font-semibold">
        {['ALL', 'PENDING', 'MATCHING', 'CONFIRMED', 'IN_PROGRESS', 'FULFILLED', 'CANCELLED'].map((status) => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              statusFilter === status
                ? 'bg-primary text-primary-foreground font-bold'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            }`}
          >
            {status}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3 text-muted-foreground">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            <p className="text-sm font-medium">Loading requisitions log...</p>
          </div>
        </div>
      ) : filteredRequests.length > 0 ? (
        <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-border bg-muted/40 text-xs font-semibold text-muted-foreground uppercase">
                <tr>
                  <th className="px-4 py-3">Requisition ID</th>
                  <th className="px-4 py-3">Blood Type</th>
                  <th className="px-4 py-3">Units Required</th>
                  <th className="px-4 py-3">Urgency</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Created</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredRequests.map((r) => (
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
                      {r.created_at ? new Date(r.created_at).toLocaleString() : 'Just now'}
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
                No requisitions found
              </h3>
              <p className="text-xs text-muted-foreground mt-1">
                {statusFilter === 'ALL'
                  ? 'No emergency requisitions have been placed for this hospital facility yet.'
                  : `No requisitions currently match the '${statusFilter}' status filter.`}
              </p>
            </div>
            <Button
              variant="danger"
              size="sm"
              onClick={() => setModalOpen(true)}
              className="mt-2"
            >
              🚨 Create Emergency Requisition
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Create Hospital Emergency Requisition"
      >
        <form onSubmit={handleCreateRequest} className="space-y-4">
          {submitSuccess && (
            <div className="p-3 rounded-lg border border-success/30 bg-success-subtle text-success text-xs font-semibold">
              {submitSuccess}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Blood Type Needed *</label>
              <select
                value={reqForm.blood_type}
                onChange={(e) => setReqForm({ ...reqForm, blood_type: e.target.value })}
                className="w-full h-10 px-3 rounded-lg border border-border bg-background text-foreground text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'].map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Units Required (1-20) *</label>
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
            <label className="text-xs font-medium text-foreground">Clinical Urgency *</label>
            <select
              value={reqForm.urgency_level}
              onChange={(e) => setReqForm({ ...reqForm, urgency_level: e.target.value })}
              className="w-full h-10 px-3 rounded-lg border border-border bg-background text-foreground text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-primary"
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
              placeholder="e.g. O-Negative urgently needed for maternal hemorrhage"
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
            >
              Dispatch Requisition
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
