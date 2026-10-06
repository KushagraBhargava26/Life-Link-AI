'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { donorService, DonorProfileData } from '@/services/donorService';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { LocationDetector } from '@/components/ui/LocationDetector';

export default function DonorProfilePage() {
  const router = useRouter();
  const { user, clearAuth } = useAuthStore();
  const [profile, setProfile] = useState<DonorProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  
  // Dashboard data for cooldown info
  const [nextEligibleDate, setNextEligibleDate] = useState<string | null>(null);
  const [daysUntilEligible, setDaysUntilEligible] = useState<number | null>(null);
  const [eligibilityStatus, setEligibilityStatus] = useState<boolean | null>(null);

  // Form states
  const [firstName, setFirstName] = useState(user?.first_name || '');
  const [lastName, setLastName] = useState(user?.last_name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  
  const [bloodType, setBloodType] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [gender, setGender] = useState('');
  const [weightKg, setWeightKg] = useState('');
  const [addressLine, setAddressLine] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [pincode, setPincode] = useState('');
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [isAvailable, setIsAvailable] = useState(true);

  // Deletion states
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    setLoading(true);
    setLoadError(null);
    try {
      // We also need dashboard data for cooldown info
      const [profileResp, dashboardResp] = await Promise.all([
        donorService.getProfile(),
        donorService.getDashboard().catch(() => null)
      ]);
      
      if (profileResp.success && profileResp.data) {
        const p = profileResp.data;
        setProfile(p);
        setBloodType(p.blood_type);
        setCity(p.city || '');
        setState(p.state || '');
        setPincode(p.pincode || '');
        setLatitude(p.latitude ?? null);
        setLongitude(p.longitude ?? null);
        setWeightKg(p.weight_kg != null ? String(p.weight_kg) : '');
        setDateOfBirth(p.date_of_birth ? p.date_of_birth.split('T')[0] : '');
        setGender(p.gender || '');
        setAddressLine(p.address_line || '');
        setIsAvailable(p.is_available);
      } else {
        throw new Error('No donor profile was returned.');
      }
      
      if (dashboardResp?.success && dashboardResp.data) {
        setNextEligibleDate(dashboardResp.data.next_eligible_date || null);
        setDaysUntilEligible(dashboardResp.data.days_until_eligible);
        setEligibilityStatus(dashboardResp.data.is_eligible);
      } else {
        setNextEligibleDate(null);
        setDaysUntilEligible(null);
        setEligibilityStatus(null);
      }
    } catch {
      setLoadError('Could not load your donor profile. Your saved information has not been changed. Try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      const resp = await donorService.updateProfile({
        blood_type: bloodType,
        city,
        state,
        pincode,
        latitude: latitude ?? undefined,
        longitude: longitude ?? undefined,
        weight_kg: Number(weightKg),
        date_of_birth: dateOfBirth || undefined,
        gender: gender || undefined,
        address_line: addressLine,
        is_available: isAvailable,
      });

      if (resp.success) {
        setMessage({ type: 'success', text: 'Profile updated successfully.' });
        setProfile(resp.data);
      } else {
        setMessage({ type: 'error', text: resp.message || 'Profile could not be updated.' });
      }
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: err.response?.data?.error?.message || 'Failed to update profile.',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE') return;
    setIsDeleting(true);
    try {
      await donorService.deleteDonorAccount();
      localStorage.removeItem('lifelink_token');
      clearAuth();
      router.push('/login');
    } catch (err: any) {
      setMessage({ type: 'error', text: 'Failed to delete account.' });
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        <p className="text-xs text-muted-foreground">Loading profile...</p>
      </div>
    );
  }

  if (loadError) {
    return (
      <Card role="alert" className="mx-auto max-w-xl">
        <CardHeader><CardTitle>Donor profile unavailable</CardTitle><CardDescription>{loadError}</CardDescription></CardHeader>
        <CardContent><Button type="button" onClick={() => void fetchProfileData()} isLoading={loading}>Try again</Button></CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
            Donor Profile
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your personal details and blood donation eligibility.
          </p>
        </div>
      </div>

      {message && (
        <div role={message.type === 'success' ? 'status' : 'alert'} className={`p-4 rounded-xl border text-sm ${message.type === 'success' ? 'border-success/30 bg-success-subtle text-success' : 'border-critical/30 bg-critical-subtle text-critical'}`}>
          {message.text}
        </div>
      )}

      {/* Cooldown Info */}
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader>
          <CardTitle className="text-lg flex items-center justify-between">
            <span>Donation Eligibility</span>
            {eligibilityStatus === true ? (
              <Badge variant="success">Eligible Now</Badge>
            ) : daysUntilEligible !== null && daysUntilEligible > 0 ? (
              <Badge variant="warning">In Cooldown</Badge>
            ) : (
              <Badge variant="outline">Not confirmed</Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-foreground">
            {eligibilityStatus === true
              ? 'The donor service currently marks your eligibility as confirmed.'
              : daysUntilEligible !== null && daysUntilEligible > 0
                ? `The donor service reports ${daysUntilEligible} days remaining${nextEligibleDate ? `, with a next eligible date of ${new Date(nextEligibleDate).toLocaleDateString()}` : ''}.`
                : eligibilityStatus === false
                  ? 'The donor service has not confirmed eligibility for this profile.'
                  : 'Eligibility information is unavailable.'}
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            This status is based on the profile and donation information currently recorded by the service.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Donation record</CardTitle><CardDescription>Summary fields returned by your donor profile.</CardDescription></CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div><p className="text-xs font-medium text-muted-foreground">Total donations recorded</p><p className="mt-1 text-lg font-semibold">{profile?.total_donations ?? 'Unavailable'}</p></div>
          <div><p className="text-xs font-medium text-muted-foreground">Last donation date</p><p className="mt-1 text-sm font-medium">{profile?.last_donation_date ? new Date(profile.last_donation_date).toLocaleDateString() : 'No date recorded'}</p></div>
          <p className="text-xs text-muted-foreground sm:col-span-2">A detailed donation history is not provided by the current donor API.</p>
        </CardContent>
      </Card>

      <form onSubmit={handleSaveProfile} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="profile-first-name" className="text-sm font-medium mb-1 block">First name (from account)</label>
                <Input id="profile-first-name" autoComplete="given-name" value={firstName} disabled />
              </div>
              <div>
                <label htmlFor="profile-last-name" className="text-sm font-medium mb-1 block">Last name (from account)</label>
                <Input id="profile-last-name" autoComplete="family-name" value={lastName} disabled />
              </div>
              <div>
                <label htmlFor="profile-phone" className="text-sm font-medium mb-1 block">Phone (from account)</label>
                <Input id="profile-phone" autoComplete="tel" value={phone} disabled />
              </div>
              <div>
                <label htmlFor="profile-date-of-birth" className="text-sm font-medium mb-1 block">Date of birth</label>
                <Input id="profile-date-of-birth" type="date" autoComplete="bday" value={dateOfBirth} onChange={(e) => setDateOfBirth(e.target.value)} required />
              </div>
              <div>
                <label htmlFor="profile-gender" className="text-sm font-medium mb-1 block">Gender (optional)</label>
                <select id="profile-gender" value={gender} onChange={(e) => setGender(e.target.value)} className="w-full min-h-11 px-3 rounded-lg border border-border bg-background text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary">
                  <option value="">Prefer not to provide</option>
                  <option value="MALE">Male</option>
                  <option value="FEMALE">Female</option>
                  <option value="OTHER">Other</option>
                  <option value="PREFER_NOT_TO_SAY">Prefer not to say</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Clinical & Contact Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="profile-blood-type" className="text-sm font-medium mb-1 block">Blood type</label>
                <select id="profile-blood-type" value={bloodType} onChange={(e) => setBloodType(e.target.value)} className="w-full min-h-11 px-3 rounded-lg border border-border bg-background text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary">
                  {['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'].map(bg => <option key={bg} value={bg}>{bg}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="profile-weight" className="text-sm font-medium mb-1 block">Weight (kg)</label>
                <Input id="profile-weight" type="number" min="45" max="250" value={weightKg} onChange={(e) => setWeightKg(e.target.value)} required />
              </div>
              <div className="md:col-span-2 pb-1 pt-1">
                <LocationDetector
                  currentCoordinates={{ latitude, longitude }}
                  onLocationDetected={(loc) => {
                    if (loc.address_line) setAddressLine(loc.address_line);
                    if (loc.city) setCity(loc.city);
                    if (loc.state) setState(loc.state);
                    if (loc.pincode) setPincode(loc.pincode);
                    setLatitude(loc.latitude);
                    setLongitude(loc.longitude);
                  }}
                />
              </div>

              <div className="md:col-span-2">
                <label htmlFor="profile-address" className="text-sm font-medium mb-1 block">Address line</label>
                <Input id="profile-address" autoComplete="street-address" value={addressLine} onChange={(e) => setAddressLine(e.target.value)} />
              </div>
              <div>
                <label htmlFor="profile-city" className="text-sm font-medium mb-1 block">City</label>
                <Input id="profile-city" autoComplete="address-level2" value={city} onChange={(e) => setCity(e.target.value)} required />
              </div>
              <div>
                <label htmlFor="profile-state" className="text-sm font-medium mb-1 block">State</label>
                <Input id="profile-state" autoComplete="address-level1" value={state} onChange={(e) => setState(e.target.value)} required />
              </div>
              <div>
                <label htmlFor="profile-pincode" className="text-sm font-medium mb-1 block">PIN code</label>
                <Input id="profile-pincode" inputMode="numeric" autoComplete="postal-code" value={pincode} onChange={(e) => setPincode(e.target.value)} required />
              </div>
            </div>
            
            <div className="pt-4 flex items-center gap-2">
              <input type="checkbox" id="availability" checked={isAvailable} onChange={(e) => setIsAvailable(e.target.checked)} className="h-5 w-5 rounded border-border text-primary focus:ring-primary" />
              <label htmlFor="availability" className="flex min-h-11 items-center text-sm font-medium">Available for emergency requests</label>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button type="submit" variant="primary" isLoading={saving}>Save Profile</Button>
        </div>
      </form>

      {/* Account Deletion */}
      <Card className="border-critical/30 mt-12">
        <CardHeader>
          <CardTitle className="text-critical">Danger Zone</CardTitle>
          <CardDescription>Permanently delete your account and all associated data.</CardDescription>
        </CardHeader>
        <CardContent>
          {!showDeleteConfirm ? (
            <Button variant="danger" onClick={() => setShowDeleteConfirm(true)}>Delete Account</Button>
          ) : (
            <div className="space-y-4 max-w-sm p-4 bg-critical/5 rounded-lg border border-critical/20">
              <p className="text-sm font-semibold text-critical">Type DELETE to confirm.</p>
              <label htmlFor="delete-confirm" className="block text-sm font-medium">Confirmation text</label>
              <Input id="delete-confirm" autoComplete="off" value={deleteConfirmText} onChange={(e) => setDeleteConfirmText(e.target.value)} placeholder="Type DELETE" />
              <div className="flex gap-2">
                <Button variant="danger" onClick={handleDeleteAccount} disabled={deleteConfirmText !== 'DELETE'} isLoading={isDeleting}>Confirm Deletion</Button>
                <Button variant="outline" onClick={() => {setShowDeleteConfirm(false); setDeleteConfirmText('');}}>Cancel</Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
