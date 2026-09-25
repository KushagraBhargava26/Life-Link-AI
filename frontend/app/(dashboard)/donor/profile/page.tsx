'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { donorService, DonorProfileData } from '@/services/donorService';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';

export default function DonorProfilePage() {
  const router = useRouter();
  const { user, clearAuth } = useAuthStore();
  const [profile, setProfile] = useState<DonorProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // Dashboard data for cooldown info
  const [nextEligibleDate, setNextEligibleDate] = useState<string | null>(null);
  const [daysUntilEligible, setDaysUntilEligible] = useState<number>(0);

  // Form states
  const [firstName, setFirstName] = useState(user?.first_name || '');
  const [lastName, setLastName] = useState(user?.last_name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  
  const [bloodType, setBloodType] = useState('O+');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [gender, setGender] = useState('MALE');
  const [weightKg, setWeightKg] = useState('65');
  const [addressLine, setAddressLine] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [pincode, setPincode] = useState('');
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
        setWeightKg(p.weight_kg ? String(p.weight_kg) : '65');
        setDateOfBirth(p.date_of_birth ? p.date_of_birth.split('T')[0] : '');
        setGender(p.gender || 'MALE');
        setAddressLine(p.address_line || '');
        setIsAvailable(p.is_available);
      }
      
      if (dashboardResp?.success && dashboardResp.data) {
        setNextEligibleDate(dashboardResp.data.next_eligible_date || null);
        setDaysUntilEligible(dashboardResp.data.days_until_eligible || 0);
      }
    } catch (err) {
      console.error("Failed to load profile", err);
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
        weight_kg: Number(weightKg),
        date_of_birth: dateOfBirth || undefined,
        gender,
        address_line: addressLine,
        is_available: isAvailable,
      });

      if (resp.success) {
        setMessage({ type: 'success', text: 'Profile updated successfully.' });
        setProfile(resp.data);
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

  const genderCooldownDays = gender === 'FEMALE' ? 112 : 84;

  return (
    <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">
            Donor Profile
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your personal details and blood donation eligibility.
          </p>
        </div>
      </div>

      {message && (
        <div className={`p-4 rounded-xl border text-sm ${message.type === 'success' ? 'border-success/30 bg-success-subtle text-success' : 'border-critical/30 bg-critical-subtle text-critical'}`}>
          {message.text}
        </div>
      )}

      {/* Cooldown Info */}
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader>
          <CardTitle className="text-lg flex items-center justify-between">
            <span>Donation Eligibility</span>
            {daysUntilEligible === 0 ? (
              <Badge variant="success">Eligible Now</Badge>
            ) : (
              <Badge variant="warning">In Cooldown</Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-foreground">
            {daysUntilEligible > 0 
              ? `You are in cooldown. Next eligible date: ${new Date(nextEligibleDate!).toLocaleDateString()} (${daysUntilEligible} days left).`
              : 'You are medically eligible to donate blood.'}
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            As a {gender.toLowerCase()} donor, you must wait {genderCooldownDays} days between donations (WHO standard).
          </p>
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
                <label className="text-xs font-semibold mb-1 block">First Name (from account)</label>
                <Input value={firstName} disabled />
              </div>
              <div>
                <label className="text-xs font-semibold mb-1 block">Last Name (from account)</label>
                <Input value={lastName} disabled />
              </div>
              <div>
                <label className="text-xs font-semibold mb-1 block">Phone (from account)</label>
                <Input value={phone} disabled />
              </div>
              <div>
                <label className="text-xs font-semibold mb-1 block">Date of Birth</label>
                <Input type="date" value={dateOfBirth} onChange={(e) => setDateOfBirth(e.target.value)} required />
              </div>
              <div>
                <label className="text-xs font-semibold mb-1 block">Gender</label>
                <select value={gender} onChange={(e) => setGender(e.target.value)} className="w-full h-10 px-3 rounded-lg border border-border bg-background text-sm focus:ring-2 focus:ring-primary">
                  <option value="MALE">Male</option>
                  <option value="FEMALE">Female</option>
                  <option value="OTHER">Other</option>
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
                <label className="text-xs font-semibold mb-1 block">Blood Type</label>
                <select value={bloodType} onChange={(e) => setBloodType(e.target.value)} className="w-full h-10 px-3 rounded-lg border border-border bg-background text-sm focus:ring-2 focus:ring-primary">
                  {['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'].map(bg => <option key={bg} value={bg}>{bg}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold mb-1 block">Weight (kg)</label>
                <Input type="number" min="45" max="250" value={weightKg} onChange={(e) => setWeightKg(e.target.value)} required />
              </div>
              <div className="md:col-span-2">
                <label className="text-xs font-semibold mb-1 block">Address Line</label>
                <Input value={addressLine} onChange={(e) => setAddressLine(e.target.value)} />
              </div>
              <div>
                <label className="text-xs font-semibold mb-1 block">City</label>
                <Input value={city} onChange={(e) => setCity(e.target.value)} required />
              </div>
              <div>
                <label className="text-xs font-semibold mb-1 block">State</label>
                <Input value={state} onChange={(e) => setState(e.target.value)} required />
              </div>
              <div>
                <label className="text-xs font-semibold mb-1 block">Pincode</label>
                <Input value={pincode} onChange={(e) => setPincode(e.target.value)} required />
              </div>
            </div>
            
            <div className="pt-4 flex items-center gap-2">
              <input type="checkbox" id="availability" checked={isAvailable} onChange={(e) => setIsAvailable(e.target.checked)} className="h-4 w-4 rounded border-border text-primary focus:ring-primary" />
              <label htmlFor="availability" className="text-sm font-medium">Available for Emergency Calls</label>
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
              <Input value={deleteConfirmText} onChange={(e) => setDeleteConfirmText(e.target.value)} placeholder="DELETE" />
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
