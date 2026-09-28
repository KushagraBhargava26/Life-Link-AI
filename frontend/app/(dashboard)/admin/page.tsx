'use client';

// frontend/app/(dashboard)/admin/page.tsx
// LifeLink AI — Admin Governance & Facility Management Console
// Architecture Reference: ARCHITECTURE.md Section 22

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { adminService, type AdminFacility, type AdminFacilityListResponse } from '@/services/adminService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';

export default function AdminDashboardPage() {
  const router = useRouter();
  const { isAuthenticated, user, isLoading: authLoading } = useAuthStore();

  const [data, setData] = useState<AdminFacilityListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [activeTab, setActiveTab] = useState<'hospitals' | 'blood_banks'>('hospitals');
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [previewCert, setPreviewCert] = useState<{ name: string; url: string } | null>(null);
  const [pendingStatus, setPendingStatus] = useState<{ facilityType: 'hospital' | 'blood_bank'; facilityId: string; name: string; status: 'ACTIVE' | 'SUSPENDED' | 'BLOCKED' } | null>(null);

  const loadFacilities = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await adminService.getAllFacilities(statusFilter === 'ALL' ? undefined : statusFilter);
      setData(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load facilities. Please verify your admin privileges.');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated || !user) {
      router.replace('/admin/login');
      return;
    }
    const roles = user.roles || (user.role ? [user.role] : []);
    if (!roles.includes('SUPER_ADMIN') && !roles.includes('ADMIN')) {
      router.replace('/login');
      return;
    }
    loadFacilities();
  }, [isAuthenticated, user, authLoading, router, loadFacilities]);

  const handleStatusChange = async () => {
    if (!pendingStatus) return;
    try {
      setActionLoading(`${pendingStatus.facilityType}-${pendingStatus.facilityId}`);
      if (pendingStatus.facilityType === 'hospital') {
        await adminService.updateHospitalStatus(pendingStatus.facilityId, pendingStatus.status, `Status updated to ${pendingStatus.status} via Admin Console`);
      } else {
        await adminService.updateBloodBankStatus(pendingStatus.facilityId, pendingStatus.status, `Status updated to ${pendingStatus.status} via Admin Console`);
      }
      setPendingStatus(null);
      await loadFacilities();
    } catch (err: any) {
      setError(err?.message || 'Could not update facility status. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };

  const currentList = activeTab === 'hospitals' ? data?.hospitals || [] : data?.blood_banks || [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl">🛡️</span>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              Platform Governance &amp; Facility Oversight
            </h1>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Review facility records and manage operational status.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={loadFacilities} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh Directory'}
          </Button>
        </div>
      </div>

      {/* Metrics Summary Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="border-border/80 bg-card">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs">Active Facilities</CardDescription>
            <CardTitle className="text-2xl font-bold text-green-600 dark:text-green-400">
              {data?.total_active ?? 'Unavailable'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-[11px] text-muted-foreground">Facilities marked active in the service</p>
          </CardContent>
        </Card>

        <Card className="border-border/80 bg-card">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs">Suspended Facilities</CardDescription>
            <CardTitle className="text-2xl font-bold text-amber-500">
              {data?.total_suspended ?? 'Unavailable'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-[11px] text-muted-foreground">Facilities marked suspended</p>
          </CardContent>
        </Card>

        <Card className="border-border/80 bg-card">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs">Blocked Facilities</CardDescription>
            <CardTitle className="text-2xl font-bold text-red-500">
              {data?.total_blocked ?? 'Unavailable'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-[11px] text-muted-foreground">Facilities marked blocked</p>
          </CardContent>
        </Card>
      </div>

      {/* Controls & Tab Navigation */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Button
            variant={activeTab === 'hospitals' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('hospitals')}
            aria-pressed={activeTab === 'hospitals'}
            className="text-xs"
          >
            Hospitals ({data?.hospitals.length ?? 0})
          </Button>
          <Button
            variant={activeTab === 'blood_banks' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('blood_banks')}
            aria-pressed={activeTab === 'blood_banks'}
            className="text-xs"
          >
            Blood Banks ({data?.blood_banks.length ?? 0})
          </Button>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-muted-foreground font-medium">Filter Status:</span>
          {['ALL', 'ACTIVE', 'SUSPENDED', 'BLOCKED'].map((st) => (
            <button
              key={st}
              type="button"
              aria-pressed={statusFilter === st}
              onClick={() => setStatusFilter(st)}
              className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${
                statusFilter === st
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted/50 text-muted-foreground hover:text-foreground'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-600 dark:text-red-400 flex flex-col items-start gap-3 sm:flex-row sm:items-center sm:justify-between">
          <span>{error}</span>
          <Button type="button" size="sm" variant="outline" onClick={() => void loadFacilities()} isLoading={loading}>Try again</Button>
        </div>
      )}

      {/* Facility List Table */}
      {loading ? (
        <div className="p-12 text-center text-xs text-muted-foreground">Loading facility registry...</div>
      ) : error ? null : currentList.length === 0 ? (
        <Card className="border-dashed border-border/80">
          <CardContent className="p-12 text-center space-y-2">
            <p className="text-sm font-semibold text-foreground">No facilities found</p>
            <p className="text-xs text-muted-foreground">No {activeTab} match the selected status filter.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {currentList.map((fac) => {
            const isHosp = activeTab === 'hospitals';
            const actionId = `${isHosp ? 'hospital' : 'blood_bank'}-${fac.id}`;
            const isProcessing = actionLoading === actionId;

            return (
              <Card key={fac.id} className="border-border/80 bg-card overflow-hidden">
                <div className="p-5 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-base font-bold text-foreground tracking-tight">{fac.name}</h3>
                      {fac.is_verified && (
                        <span className="inline-flex items-center gap-1 rounded bg-green-500/10 px-2 py-0.5 text-[11px] font-semibold text-green-600 dark:text-green-400">
                          ✓ Verified
                        </span>
                      )}
                      <span
                        className={`inline-flex items-center rounded px-2 py-0.5 text-[11px] font-bold ${
                          fac.status === 'ACTIVE'
                            ? 'bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/20'
                            : fac.status === 'SUSPENDED'
                            ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
                            : 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20'
                        }`}
                      >
                        {fac.status}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-xs text-muted-foreground pt-1">
                      <div>
                        <span className="font-semibold text-foreground">Location:</span> {fac.city}, {fac.state}
                      </div>
                      <div>
                        <span className="font-semibold text-foreground">Reg/License:</span>{' '}
                        {fac.registration_number || fac.license_number || 'N/A'}
                      </div>
                      <div>
                        <span className="font-semibold text-foreground">Contact:</span> {fac.phone}
                      </div>
                      <div>
                        <span className="font-semibold text-foreground">License Issue:</span>{' '}
                        {fac.license_issue_date || 'N/A'}
                      </div>
                      <div>
                        <span className="font-semibold text-foreground">License Expiry:</span>{' '}
                        {fac.license_expiry_date || 'N/A'}
                      </div>
                      <div>
                        <span className="font-semibold text-foreground">Certificate:</span>{' '}
                        {fac.certificate_url ? (
                          <button
                            onClick={() => setPreviewCert({ name: fac.name, url: fac.certificate_url! })}
                            className="text-primary hover:underline font-semibold"
                          >
                            View Document
                          </button>
                        ) : (
                          <span className="text-muted-foreground/60">No file uploaded</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Operational Action Buttons */}
                  <div className="flex flex-wrap items-center gap-2 pt-2 lg:pt-0 border-t lg:border-t-0 border-border/50">
                    {fac.status !== 'ACTIVE' && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-xs text-green-600 border-green-500/30 hover:bg-green-500/10"
                        disabled={isProcessing}
                            onClick={() => setPendingStatus({ facilityType: isHosp ? 'hospital' : 'blood_bank', facilityId: fac.id, name: fac.name, status: 'ACTIVE' })}
                      >
                        {isProcessing ? 'Updating...' : 'Activate Facility'}
                      </Button>
                    )}
                    {fac.status !== 'SUSPENDED' && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-xs text-amber-600 border-amber-500/30 hover:bg-amber-500/10"
                        disabled={isProcessing}
                            onClick={() => setPendingStatus({ facilityType: isHosp ? 'hospital' : 'blood_bank', facilityId: fac.id, name: fac.name, status: 'SUSPENDED' })}
                      >
                        {isProcessing ? 'Updating...' : 'Suspend Facility'}
                      </Button>
                    )}
                    {fac.status !== 'BLOCKED' && (
                      <Button
                        variant="danger"
                        size="sm"
                        className="text-xs"
                        disabled={isProcessing}
                        onClick={() => setPendingStatus({ facilityType: isHosp ? 'hospital' : 'blood_bank', facilityId: fac.id, name: fac.name, status: 'BLOCKED' })}
                      >
                        {isProcessing ? 'Updating...' : 'Block Facility'}
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Certificate Viewer Modal */}
      <Modal isOpen={previewCert !== null} onClose={() => setPreviewCert(null)} title="Certificate reference">
        {previewCert && <div className="space-y-4">
          <p className="text-sm text-foreground">{previewCert.name}</p>
          <p className="break-all rounded-lg border border-border bg-muted/20 p-4 font-mono text-xs text-muted-foreground">{previewCert.url}</p>
          <p className="text-xs text-muted-foreground">This page displays the saved reference only. It does not open or independently verify the document.</p>
        </div>}
      </Modal>

      <Modal isOpen={pendingStatus !== null} onClose={() => { if (!actionLoading) setPendingStatus(null); }} title="Confirm facility status change">
        {pendingStatus && <div className="space-y-4">
          <p className="text-sm text-muted-foreground">Change {pendingStatus.name} to <strong className="text-foreground">{pendingStatus.status}</strong>? This status update will be submitted to the administration service.</p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button type="button" variant="outline" onClick={() => setPendingStatus(null)} disabled={actionLoading !== null}>Cancel</Button>
            <Button type="button" variant={pendingStatus.status === 'BLOCKED' ? 'danger' : 'primary'} onClick={() => void handleStatusChange()} isLoading={actionLoading !== null}>Confirm status change</Button>
          </div>
        </div>}
      </Modal>
    </div>
  );
}
