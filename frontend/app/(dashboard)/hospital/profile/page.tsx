'use client';

// frontend/app/(dashboard)/hospital/profile/page.tsx
// LifeLink AI — Hospital Facility Profile Management
// Architecture Reference: ARCHITECTURE.md Section 15, 27; DATABASE.md Section 7

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { hospitalService } from '@/services/hospitalService';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import type { Hospital, HospitalCreateData, HospitalType } from '@/types';

export default function HospitalProfilePage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const [hospital, setHospital] = useState<Hospital | null>(null);
  const [isExisting, setIsExisting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Deletion states
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  const [formData, setFormData] = useState<HospitalCreateData>({
    name: '',
    registration_number: '',
    type: 'PRIVATE',
    address_line: '',
    city: '',
    state: '',
    pincode: '',
    phone: '',
    email: '',
    website: '',
    bed_count: undefined,
    has_blood_bank: false,
    license_issue_date: '',
    license_expiry_date: '',
    certificate_url: '',
  });

  useEffect(() => {
    async function fetchProfile() {
      try {
        const data = await hospitalService.getMyProfile();
        setHospital(data);
        setIsExisting(true);
        setFormData({
          name: data.name,
          registration_number: data.registration_number || '',
          type: data.type,
          address_line: data.address_line,
          city: data.city,
          state: data.state,
          pincode: data.pincode,
          phone: data.phone,
          email: data.email || '',
          website: data.website || '',
          bed_count: data.bed_count || undefined,
          has_blood_bank: data.has_blood_bank,
          license_issue_date: data.license_issue_date || '',
          license_expiry_date: data.license_expiry_date || '',
          certificate_url: data.certificate_url || '',
        });
      } catch (err: any) {
        if (err.response?.status === 404) {
          setIsExisting(false);
        } else {
          setMessage({ type: 'error', text: 'Failed to load hospital facility profile.' });
        }
      } finally {
        setIsLoading(false);
      }
    }

    if (isAuthenticated) {
      fetchProfile();
    }
  }, [isAuthenticated]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage(null);

    try {
      const payload: any = {
        name: formData.name.trim(),
        registration_number: formData.registration_number?.trim() || undefined,
        type: formData.type,
        address_line: formData.address_line.trim(),
        city: formData.city.trim(),
        state: formData.state.trim(),
        pincode: formData.pincode.trim(),
        phone: formData.phone.trim(),
        email: formData.email?.trim() || undefined,
        website: formData.website?.trim() || undefined,
        bed_count: formData.bed_count ? Number(formData.bed_count) : undefined,
        has_blood_bank: Boolean(formData.has_blood_bank),
        license_issue_date: formData.license_issue_date || undefined,
        license_expiry_date: formData.license_expiry_date || undefined,
        certificate_url: formData.certificate_url?.trim() || undefined,
      };

      if (isExisting) {
        const updated = await hospitalService.updateProfile(payload);
        setHospital(updated);
        setMessage({ type: 'success', text: 'Hospital facility profile updated successfully.' });
      } else {
        const created = await hospitalService.createProfile(payload);
        setHospital(created);
        setIsExisting(true);
        setMessage({ type: 'success', text: 'Hospital facility registered and activated successfully!' });
      }
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: err.response?.data?.error?.message || 'Failed to save hospital profile.',
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="flex flex-col items-center gap-3 text-muted-foreground">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm font-medium">Loading hospital profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              {isExisting ? 'Facility Profile & Settings' : 'Register Hospital Facility'}
            </h1>
            {isExisting && (
              hospital?.is_verified ? (
                <Badge variant="success" size="sm">Verified &amp; Active</Badge>
              ) : (
                <Badge variant="warning" size="sm">Verification Pending</Badge>
              )
            )}
          </div>
          <p className="text-sm text-muted-foreground">
            Official registration and clinical operational capacity for trauma coordination. Complete registration activates facility features immediately.
          </p>
        </div>

        {isExisting && (
          <Link href="/hospital">
            <Button variant="secondary" size="sm">
              &larr; Back to Dashboard
            </Button>
          </Link>
        )}
      </div>

      {message && (
        <div
          className={`p-4 rounded-xl border text-sm ${
            message.type === 'success'
              ? 'border-success/30 bg-success-subtle text-success font-medium'
              : 'border-critical/30 bg-critical-subtle text-critical'
          }`}
        >
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Facility Information */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Institutional Identification &amp; Statutory Licensing</CardTitle>
            <CardDescription className="text-xs">
              Primary healthcare institution registration, clinical bed count, and statutory state health license.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Hospital Name *</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Apollo Apex Care Hospital"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Registration / License Number *</label>
                <Input
                  value={formData.registration_number || ''}
                  onChange={(e) => setFormData({ ...formData, registration_number: e.target.value })}
                  placeholder="e.g. MH-MUM-2024-8841"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Facility Type *</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value as HospitalType })}
                  className="w-full h-10 px-3 rounded-lg border border-border bg-background text-foreground text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="GOVERNMENT">GOVERNMENT — State / Central Public Hospital</option>
                  <option value="PRIVATE">PRIVATE — Private Tertiary Care Center</option>
                  <option value="TRUST">TRUST — Non-profit / Charitable Trust</option>
                  <option value="SPECIALTY">SPECIALTY — Dedicated Trauma / Cardiac Hospital</option>
                  <option value="CLINIC">CLINIC — Day-care / Surgical Clinic</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Registered Inpatient Bed Count</label>
                <Input
                  type="number"
                  min="1"
                  value={formData.bed_count || ''}
                  onChange={(e) => setFormData({ ...formData, bed_count: e.target.value ? Number(e.target.value) : undefined })}
                  placeholder="e.g. 450"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">License Issue Date</label>
                <Input
                  type="date"
                  value={formData.license_issue_date || ''}
                  onChange={(e) => setFormData({ ...formData, license_issue_date: e.target.value })}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">License Expiry Date</label>
                <Input
                  type="date"
                  value={formData.license_expiry_date || ''}
                  onChange={(e) => setFormData({ ...formData, license_expiry_date: e.target.value })}
                />
              </div>

              <div className="md:col-span-2 space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Statutory Certificate URL / Document Reference</label>
                <Input
                  value={formData.certificate_url || ''}
                  onChange={(e) => setFormData({ ...formData, certificate_url: e.target.value })}
                  placeholder="e.g. /uploads/certificates/apollo_apex_license.pdf"
                  helperText="Uploaded certificate or State Health Registry document for verification audit."
                />
              </div>
            </div>

            <div className="pt-2">
              <label className="flex items-center gap-2 cursor-pointer text-sm font-medium text-foreground">
                <input
                  type="checkbox"
                  checked={formData.has_blood_bank}
                  onChange={(e) => setFormData({ ...formData, has_blood_bank: e.target.checked })}
                  className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                />
                <span>Hospital operates an active on-premise blood bank facility</span>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Location & Contact Information */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Location &amp; Emergency Dispatch Contact</CardTitle>
            <CardDescription className="text-xs">
              Physical address used by voluntary blood donors and emergency courier units.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-foreground">Street Address / Facility Campus *</label>
              <Input
                value={formData.address_line}
                onChange={(e) => setFormData({ ...formData, address_line: e.target.value })}
                placeholder="e.g. Sector 12, Ring Road"
                required
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">City *</label>
                <Input
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  placeholder="e.g. Mumbai"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">State *</label>
                <Input
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  placeholder="e.g. Maharashtra"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">PIN Code *</label>
                <Input
                  value={formData.pincode}
                  onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                  placeholder="e.g. 400001"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Emergency Desk Phone *</label>
                <Input
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+91 22 2675 1000"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Official Email</label>
                <Input
                  type="email"
                  value={formData.email || ''}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="trauma@hospital.org"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Website</label>
                <Input
                  value={formData.website || ''}
                  onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                  placeholder="https://hospital.org"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Submit Actions */}
        <div className="flex items-center justify-end gap-3 pt-4">
          <Button
            type="submit"
            variant="primary"
            size="md"
            isLoading={isSaving}
            className="shadow-sm"
          >
            {isExisting ? 'Save Facility Changes' : 'Register Hospital Facility'}
          </Button>
        </div>
      </form>

      {isExisting && (
        <Card className="border-critical/30 mt-8">
          <CardHeader>
            <CardTitle className="text-critical">Danger Zone</CardTitle>
            <CardDescription>Permanently delete your hospital facility account and all associated operational records.</CardDescription>
          </CardHeader>
          <CardContent>
            {!showDeleteConfirm ? (
              <Button variant="danger" onClick={() => setShowDeleteConfirm(true)}>
                Delete Hospital Account
              </Button>
            ) : (
              <div className="space-y-4 max-w-md p-4 bg-critical/5 rounded-lg border border-critical/20">
                <p className="text-sm font-semibold text-critical">
                  Warning: This action will permanently deactivate your hospital facility. Type DELETE to confirm.
                </p>
                <Input
                  value={deleteConfirmText}
                  onChange={(e) => setDeleteConfirmText(e.target.value)}
                  placeholder="DELETE"
                />
                <div className="flex gap-2">
                  <Button
                    variant="danger"
                    disabled={deleteConfirmText !== 'DELETE'}
                    isLoading={isDeleting}
                    onClick={async () => {
                      if (deleteConfirmText !== 'DELETE') return;
                      setIsDeleting(true);
                      try {
                        await hospitalService.deleteHospitalAccount();
                        localStorage.removeItem('lifelink_token');
                        useAuthStore.getState().clearAuth();
                        router.push('/login');
                      } catch (e: any) {
                        setMessage({ type: 'error', text: e?.response?.data?.error?.message || 'Failed to delete hospital account.' });
                        setIsDeleting(false);
                        setShowDeleteConfirm(false);
                      }
                    }}
                  >
                    Confirm Deletion
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowDeleteConfirm(false);
                      setDeleteConfirmText('');
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
