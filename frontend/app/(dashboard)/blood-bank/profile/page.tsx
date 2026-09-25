'use client';

// frontend/app/(dashboard)/blood-bank/profile/page.tsx
// LifeLink AI — Blood Bank Facility Profile Management
// Architecture Reference: ARCHITECTURE.md Section 15, 27; DATABASE.md Section 8

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { bloodBankService } from '@/services/bloodBankService';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import type { BloodBank, BloodBankCreateData } from '@/types';

export default function BloodBankProfilePage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [bank, setBank] = useState<BloodBank | null>(null);
  const [isExisting, setIsExisting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Deletion states
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  const [formData, setFormData] = useState<BloodBankCreateData>({
    name: '',
    license_number: '',
    address_line: '',
    city: '',
    state: '',
    pincode: '',
    phone: '',
    email: '',
    operating_hours: '',
    is_24_hours: false,
    accepts_walk_in: true,
    license_issue_date: '',
    license_expiry_date: '',
    certificate_url: '',
  });

  useEffect(() => {
    async function fetchProfile() {
      try {
        const data = await bloodBankService.getMyProfile();
        setBank(data);
        setIsExisting(true);
        setFormData({
          name: data.name,
          license_number: data.license_number || '',
          address_line: data.address_line,
          city: data.city,
          state: data.state,
          pincode: data.pincode,
          phone: data.phone,
          email: data.email || '',
          operating_hours: data.operating_hours || '',
          is_24_hours: data.is_24_hours,
          accepts_walk_in: data.accepts_walk_in,
          license_issue_date: data.license_issue_date || '',
          license_expiry_date: data.license_expiry_date || '',
          certificate_url: data.certificate_url || '',
        });
      } catch (err: any) {
        if (err.response?.status === 404) {
          setIsExisting(false);
        } else {
          setMessage({ type: 'error', text: 'Failed to load blood bank facility profile.' });
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
        license_number: formData.license_number?.trim() || undefined,
        address_line: formData.address_line.trim(),
        city: formData.city.trim(),
        state: formData.state.trim(),
        pincode: formData.pincode.trim(),
        phone: formData.phone.trim(),
        email: formData.email?.trim() || undefined,
        operating_hours: formData.operating_hours?.trim() || undefined,
        is_24_hours: Boolean(formData.is_24_hours),
        accepts_walk_in: Boolean(formData.accepts_walk_in),
        license_issue_date: formData.license_issue_date || undefined,
        license_expiry_date: formData.license_expiry_date || undefined,
        certificate_url: formData.certificate_url?.trim() || undefined,
      };

      if (isExisting) {
        const updated = await bloodBankService.updateProfile(payload);
        setBank(updated);
        setMessage({ type: 'success', text: 'Blood bank facility profile updated successfully.' });
      } else {
        const created = await bloodBankService.createProfile(payload);
        setBank(created);
        setIsExisting(true);
        setMessage({ type: 'success', text: 'Blood bank facility registered and activated successfully!' });
      }
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: err.response?.data?.error?.message || 'Failed to save blood bank profile.',
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
          <p className="text-sm font-medium">Loading blood bank facility profile...</p>
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
              {isExisting ? 'Blood Bank Facility Settings' : 'Register Blood Bank Facility'}
            </h1>
            {isExisting && (
              bank?.is_verified ? (
                <Badge variant="success" size="sm">Licensed &amp; Active</Badge>
              ) : (
                <Badge variant="warning" size="sm">Licensing Verification Pending</Badge>
              )
            )}
          </div>
          <p className="text-sm text-muted-foreground">
            Official statutory licensing credentials and emergency dispatch readiness. Complete registration activates facility operations immediately.
          </p>
        </div>

        {isExisting && (
          <Link href="/blood-bank">
            <Button variant="secondary" size="sm">
              &larr; Back to Console
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
        {/* Facility Details */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Blood Bank Registration &amp; Statutory Licensing</CardTitle>
            <CardDescription className="text-xs">
              State blood transfusion council licensing, drug controller authorization, and facility operating credentials.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Blood Bank Official Name *</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Central Red Cross Blood Center"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Drug Controller License Number *</label>
                <Input
                  value={formData.license_number || ''}
                  onChange={(e) => setFormData({ ...formData, license_number: e.target.value })}
                  placeholder="e.g. BB-MH-2024-0091"
                  required
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
                <label className="text-xs font-semibold text-foreground">Statutory Certificate URL / Document Path</label>
                <Input
                  value={formData.certificate_url || ''}
                  onChange={(e) => setFormData({ ...formData, certificate_url: e.target.value })}
                  placeholder="e.g. /uploads/certificates/redcross_bb_license.pdf"
                  helperText="State Blood Transfusion Council certificate on record."
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Standard Operating Hours</label>
                <Input
                  value={formData.operating_hours || ''}
                  onChange={(e) => setFormData({ ...formData, operating_hours: e.target.value })}
                  placeholder="e.g. 24/7 Emergency Transfusion Unit"
                />
              </div>

              <div className="space-y-3 pt-6">
                <label className="flex items-center gap-2 cursor-pointer text-sm font-medium text-foreground">
                  <input
                    type="checkbox"
                    checked={formData.is_24_hours}
                    onChange={(e) => setFormData({ ...formData, is_24_hours: e.target.checked })}
                    className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                  />
                  <span>24 / 7 Round the clock emergency transfusion service</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer text-sm font-medium text-foreground">
                  <input
                    type="checkbox"
                    checked={formData.accepts_walk_in}
                    onChange={(e) => setFormData({ ...formData, accepts_walk_in: e.target.checked })}
                    className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                  />
                  <span>Accepts voluntary walk-in donors without prior appointment</span>
                </label>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Address & Emergency Contact */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Location &amp; Dispatch Line</CardTitle>
            <CardDescription className="text-xs">
              Physical address used by logistics and clinical cold-chain transport.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-foreground">Street Address / Campus *</label>
              <Input
                value={formData.address_line}
                onChange={(e) => setFormData({ ...formData, address_line: e.target.value })}
                placeholder="e.g. 141 Shahid Bhagat Singh Road"
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

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Emergency Dispatch Hotline *</label>
                <Input
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+91 22 2266 1234"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Official Email</label>
                <Input
                  type="email"
                  value={formData.email || ''}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="dispatch@redcrossblood.org"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex items-center justify-end gap-3 pt-4">
          <Button
            type="submit"
            variant="primary"
            size="md"
            isLoading={isSaving}
            className="shadow-sm"
          >
            {isExisting ? 'Save Facility Changes' : 'Register Blood Bank'}
          </Button>
        </div>
      </form>

      {isExisting && (
        <Card className="border-critical/30 mt-8">
          <CardHeader>
            <CardTitle className="text-critical">Danger Zone</CardTitle>
            <CardDescription>Permanently delete your blood bank facility account and all associated inventory records.</CardDescription>
          </CardHeader>
          <CardContent>
            {!showDeleteConfirm ? (
              <Button variant="danger" onClick={() => setShowDeleteConfirm(true)}>
                Delete Blood Bank Account
              </Button>
            ) : (
              <div className="space-y-4 max-w-md p-4 bg-critical/5 rounded-lg border border-critical/20">
                <p className="text-sm font-semibold text-critical">
                  Warning: This action will permanently deactivate your blood bank facility. Type DELETE to confirm.
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
                        await bloodBankService.deleteBloodBankAccount();
                        localStorage.removeItem('lifelink_token');
                        useAuthStore.getState().clearAuth();
                        router.push('/login');
                      } catch (e: any) {
                        setMessage({ type: 'error', text: e?.response?.data?.error?.message || 'Failed to delete blood bank account.' });
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
