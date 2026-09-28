'use client';

// frontend/app/(dashboard)/donor/page.tsx
// LifeLink AI — Donor Dashboard, Eligibility & Emergency Readiness
// Architecture Reference: ARCHITECTURE.md Section 33

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { donorService, DonorDashboardData, DonorProfileData } from '@/services/donorService';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

export default function DonorDashboardPage() {
  const { user } = useAuthStore();

  const [dashboardData, setDashboardData] = useState<DonorDashboardData | null>(null);
  const [profile, setProfile] = useState<DonorProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toggling, setToggling] = useState(false);
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [loadFailed, setLoadFailed] = useState(false);

  // Form fields
  const [bloodType, setBloodType] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [pincode, setPincode] = useState('');
  const [weightKg, setWeightKg] = useState('');
  const [gender, setGender] = useState('');
  const [isAvailable, setIsAvailable] = useState(false);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    setErrorMessage(null);
    setLoadFailed(false);
    try {
      const resp = await donorService.getDashboard();
      if (resp.success && resp.data) {
        setDashboardData(resp.data);
        if (resp.data.profile) {
          setProfile(resp.data.profile);
          setIsAvailable(resp.data.profile.is_available);
          setBloodType(resp.data.profile.blood_type);
          setCity(resp.data.profile.city);
          if (resp.data.profile.state) setState(resp.data.profile.state);
          if (resp.data.profile.pincode) setPincode(resp.data.profile.pincode);
          if (resp.data.profile.weight_kg) setWeightKg(String(resp.data.profile.weight_kg));
          if (resp.data.profile.gender) setGender(resp.data.profile.gender);
        }
      } else {
        setLoadFailed(true);
        setErrorMessage(resp.message || 'Donor dashboard data is unavailable. Please try again.');
      }
    } catch (err: any) {
      setLoadFailed(true);
      setErrorMessage('Could not load donor dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAvailability = async () => {
    if (!profile) return;
    setToggling(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const newStatus = !profile.is_available;
      const resp = await donorService.toggleAvailability(newStatus);
      if (resp.success && resp.data) {
        setProfile(resp.data);
        if (dashboardData) {
          setDashboardData({
            ...dashboardData,
            is_available: newStatus,
            profile: resp.data,
          });
        }
        setSuccessMessage(newStatus ? 'Availability is enabled for emergency requests.' : 'Availability is paused.');
      } else {
        setErrorMessage(resp.message || 'Availability could not be updated.');
      }
    } catch (err: any) {
      setErrorMessage('Failed to update emergency availability.');
    } finally {
      setToggling(false);
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!city.trim()) {
      setErrorMessage('City is required.');
      setSaving(false);
      return;
    }

    if (!state.trim()) {
      setErrorMessage('State is required.');
      setSaving(false);
      return;
    }

    if (!pincode.trim() || !/^\d{4,10}$/.test(pincode.trim())) {
      setErrorMessage('A valid numeric pincode (4-10 digits) is required.');
      setSaving(false);
      return;
    }

    const weightNum = parseFloat(weightKg);
    if (isNaN(weightNum) || weightNum < 45 || weightNum > 250) {
      setErrorMessage('Weight must be a valid number between 45 and 250 kg for blood donation eligibility.');
      setSaving(false);
      return;
    }

    try {
      const resp = await donorService.saveProfile({
        blood_type: bloodType,
        city: city.trim(),
        state: state.trim(),
        pincode: pincode.trim(),
        weight_kg: weightNum,
        gender: gender || undefined,
        is_available: profile ? profile.is_available : isAvailable,
      });

      if (resp.success && resp.data) {
        setProfile(resp.data);
        setShowEditProfile(false);
        setSuccessMessage('Donor profile saved successfully.');
        fetchDashboard();
      } else {
        setErrorMessage(resp.message || 'Donor profile could not be saved.');
      }
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || 'Failed to save donor profile.';
      setErrorMessage(msg);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        <p className="text-xs text-muted-foreground">Loading donor dashboard &amp; clinical readiness...</p>
      </div>
    );
  }

  // Profile completion gate: if no profile exists or required fields are missing
  const isProfileComplete = Boolean(
    dashboardData?.has_profile && profile && profile.blood_type && profile.city
  );

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">🩸</span>
            <Badge variant="outline" className="text-xs uppercase tracking-wider font-bold">
              Voluntary Donor Portal
            </Badge>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
            {user?.first_name ? `${user.first_name}'s Donor Readiness` : 'Donor Dashboard'}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your emergency blood availability, view eligibility timers, and check local emergency requisitions.
          </p>
        </div>

        {isProfileComplete && (
          <div className="flex items-center gap-3">
            <Button
              variant={profile?.is_available ? 'danger' : 'outline'}
              size="md"
              onClick={handleToggleAvailability}
              isLoading={toggling}
              className="font-bold shadow-sm"
            >
                  {profile?.is_available ? 'Available for emergency requests' : 'Availability paused'}
            </Button>
            <Button
              variant="secondary"
              size="md"
              onClick={() => setShowEditProfile(!showEditProfile)}
            >
              {showEditProfile ? 'Close Editor' : 'Edit Profile'}
            </Button>
          </div>
        )}
      </div>

      {/* Notifications */}
      {errorMessage && !loadFailed && (
        <div role="alert" className="rounded-lg border border-critical/40 bg-critical/10 p-4 text-sm font-medium text-critical">
          {errorMessage}
        </div>
      )}
      {successMessage && (
        <div role="status" className="rounded-lg border border-success/30 bg-success-subtle p-4 text-sm font-medium text-success">
          {successMessage}
        </div>
      )}

      {loadFailed ? (
        <Card role="alert" className="mx-auto max-w-xl">
          <CardHeader>
            <CardTitle>Donor workspace unavailable</CardTitle>
            <CardDescription>Your profile and eligibility were not changed. Try loading them again.</CardDescription>
          </CardHeader>
          <CardContent><Button type="button" onClick={() => void fetchDashboard()} isLoading={loading}>Try again</Button></CardContent>
        </Card>
      ) : dashboardData?.has_profile === false ? (
        <Card className="mx-auto max-w-2xl border-border bg-card">
          <CardHeader className="border-b border-border pb-4">
            <CardTitle>Complete your donor profile</CardTitle>
            <CardDescription>Enter your own details. Required fields are marked; no sample values are prefilled.</CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <form onSubmit={handleSaveProfile} className="space-y-5">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="donor-blood-type" className="mb-1.5 block text-sm font-medium text-foreground">Blood type <span aria-hidden="true" className="text-critical">*</span></label>
                  <select id="donor-blood-type" autoComplete="off" value={bloodType} onChange={(e) => setBloodType(e.target.value)} className="min-h-11 w-full rounded-lg border border-border bg-card px-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" required>
                    <option value="" disabled>Select blood type</option>
                    {['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'].map((bg) => <option key={bg} value={bg}>{bg}</option>)}
                  </select>
                </div>
                <div>
                  <label htmlFor="donor-gender" className="mb-1.5 block text-sm font-medium text-foreground">Gender (optional)</label>
                  <select id="donor-gender" value={gender} onChange={(e) => setGender(e.target.value)} className="min-h-11 w-full rounded-lg border border-border bg-card px-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                    <option value="">Prefer not to provide</option>
                    <option value="MALE">Male</option><option value="FEMALE">Female</option><option value="OTHER">Other</option><option value="PREFER_NOT_TO_SAY">Prefer not to say</option>
                  </select>
                </div>
                <div><label htmlFor="donor-city" className="mb-1.5 block text-sm font-medium text-foreground">City <span aria-hidden="true" className="text-critical">*</span></label><Input id="donor-city" autoComplete="address-level2" value={city} onChange={(e) => setCity(e.target.value)} placeholder="Your city" required /></div>
                <div><label htmlFor="donor-state" className="mb-1.5 block text-sm font-medium text-foreground">State <span aria-hidden="true" className="text-critical">*</span></label><Input id="donor-state" autoComplete="address-level1" value={state} onChange={(e) => setState(e.target.value)} placeholder="Your state" required /></div>
                <div><label htmlFor="donor-pincode" className="mb-1.5 block text-sm font-medium text-foreground">PIN code <span aria-hidden="true" className="text-critical">*</span></label><Input id="donor-pincode" inputMode="numeric" autoComplete="postal-code" value={pincode} onChange={(e) => setPincode(e.target.value)} placeholder="Your PIN code" required /></div>
              <div><label htmlFor="donor-weight" className="mb-1.5 block text-sm font-medium text-foreground">Weight (kg) <span aria-hidden="true" className="text-critical">*</span></label><Input id="donor-weight" type="number" inputMode="decimal" min="45" max="250" value={weightKg} onChange={(e) => setWeightKg(e.target.value)} placeholder="Enter your current weight" required /><p className="mt-1 text-xs text-muted-foreground">The existing form requires at least 45 kg.</p></div>
              </div>
              <label htmlFor="donor-availability" className="flex min-h-11 items-center gap-3 text-sm text-foreground">
                <input id="donor-availability" type="checkbox" checked={isAvailable} onChange={(e) => setIsAvailable(e.target.checked)} className="h-5 w-5 rounded border-border text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" />
                Make me available for emergency requests
              </label>
              <Button type="submit" variant="primary" size="lg" isLoading={saving} className="w-full sm:w-auto">Save donor profile</Button>
            </form>
          </CardContent>
        </Card>
      ) : !isProfileComplete ? (
        <Card role="alert"><CardContent className="py-6 text-sm text-critical">The donor profile response is incomplete. Refresh the page or contact support.</CardContent></Card>
      ) : (
        <>
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="border-border bg-card">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Blood Group
                  </span>
                  <Badge variant="default" className="text-sm font-black px-2.5 py-0.5">
                    {profile?.blood_type}
                  </Badge>
                </div>
                <div className="text-2xl font-black text-foreground mt-2">
                  {profile?.blood_type}
                </div>
                <p className="text-[11px] text-muted-foreground mt-1">
                  Resident in {profile?.city}
                </p>
              </CardContent>
            </Card>

            <Card className="border-border bg-card">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Emergency Status
                  </span>
                  <Badge variant={profile?.is_available ? 'success' : 'outline'}>
                    {profile?.is_available ? 'Available' : 'Off Duty'}
                  </Badge>
                </div>
                <div className="text-lg font-bold text-foreground mt-2">
                  {profile?.is_available ? 'Active Standby' : 'Paused'}
                </div>
                <p className="text-[11px] text-muted-foreground mt-1">
                  {profile?.is_available ? 'Availability is enabled for requests' : 'Availability is paused'}
                </p>
              </CardContent>
            </Card>

            <Card className="border-border bg-card">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Donation Cooldown
                  </span>
                  <Badge variant={dashboardData?.is_eligible ? 'success' : 'outline'}>
                  {dashboardData?.is_eligible ? 'Eligible' : dashboardData?.days_until_eligible ? `${dashboardData.days_until_eligible} days left` : 'Not confirmed'}
                  </Badge>
                </div>
                <div className="text-lg font-bold text-foreground mt-2">
                  {dashboardData?.is_eligible
                    ? 'Eligible per current record'
                    : dashboardData?.days_until_eligible
                      ? `In cooldown (${dashboardData.days_until_eligible} days)`
                      : 'Eligibility not confirmed'}
                </div>
                <p className="text-[11px] text-muted-foreground mt-1">
                  Based on the eligibility information returned by the donor service.
                </p>
              </CardContent>
            </Card>

            <Card className="border-border bg-card">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Total Donations
                  </span>
                  <Badge variant="default">{profile?.total_donations ?? 'Unavailable'}</Badge>
                </div>
                <div className="text-2xl font-black text-foreground mt-2">
                  {profile?.total_donations ?? 'Unavailable'}
                </div>
                <p className="text-[11px] text-muted-foreground mt-1">
                  {dashboardData?.estimated_lives_saved != null ? `Estimated impact: ${dashboardData.estimated_lives_saved}` : 'Impact estimate unavailable'}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Edit Profile Section Drawer */}
          {showEditProfile && (
            <Card className="border-border bg-card shadow-sm animate-fade-in">
              <CardHeader className="border-b border-border/60 pb-3">
                <CardTitle className="text-base font-bold">Update Donor Profile</CardTitle>
                <CardDescription>Update your contact area and clinical eligibility details</CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <form onSubmit={handleSaveProfile} className="space-y-4 max-w-xl">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold mb-1 text-foreground">
                        Blood Type <span className="text-destructive">*</span>
                      </label>
                      <select
                        value={bloodType}
                        onChange={(e) => setBloodType(e.target.value)}
                        className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                      >
                        {['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'].map((bg) => (
                          <option key={bg} value={bg}>{bg}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1 text-foreground">
                        City <span className="text-destructive">*</span>
                      </label>
                      <Input
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        placeholder="e.g. Mumbai"
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs font-semibold mb-1 text-foreground">
                        State <span className="text-destructive">*</span>
                      </label>
                      <Input
                        value={state}
                        onChange={(e) => setState(e.target.value)}
                        placeholder="e.g. Maharashtra"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1 text-foreground">
                        Pincode <span className="text-destructive">*</span>
                      </label>
                      <Input
                        value={pincode}
                        onChange={(e) => setPincode(e.target.value)}
                        placeholder="e.g. 400001"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1 text-foreground">
                        Weight (kg) <span className="text-destructive">*</span>
                      </label>
                      <Input
                        type="number"
                        min="45"
                        max="250"
                        value={weightKg}
                        onChange={(e) => setWeightKg(e.target.value)}
                        placeholder="min 45"
                        required
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-3 pt-2">
                    <Button type="submit" variant="primary" size="sm" isLoading={saving} className="font-bold">
                      Save Changes
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setShowEditProfile(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {/* Compatible Emergency Opportunities in City */}
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <div>
                <h2 className="text-xl font-bold text-foreground">
                  Active Emergency Opportunities
                </h2>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Current requests returned by the matching service for your profile in {profile?.city}
                </p>
              </div>
              <Badge variant="outline">
                {dashboardData?.compatible_opportunities.length || 0} requests
              </Badge>
            </div>

            {dashboardData?.compatible_opportunities && dashboardData.compatible_opportunities.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {dashboardData.compatible_opportunities.map((opp) => (
                  <Card key={opp.id} className="border-border bg-card shadow-sm hover:border-primary/50 transition-all">
                    <CardHeader className="pb-3 border-b border-border/60">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-foreground">{opp.request_number}</span>
                        </div>
                        <Badge variant={opp.urgency_level === 'CRITICAL' ? 'critical' : opp.urgency_level === 'HIGH' ? 'high' : 'outline'} className="font-bold text-xs">
                          {opp.urgency_level} urgency
                        </Badge>
                      </div>
                      <CardTitle className="text-base font-bold text-foreground mt-2">
                        {opp.hospital_name || 'Facility name not provided'}
                      </CardTitle>
                    </CardHeader>

                    <CardContent className="pt-3.5 space-y-3">
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="p-2.5 rounded-lg bg-muted/40 border border-border/60">
                          <span className="text-[10px] uppercase font-bold text-muted-foreground block mb-0.5">
                            Blood Group Needed
                          </span>
                          <span className="text-sm font-black text-critical flex items-center gap-1">
                            <span>🩸</span>
                            <span>{opp.blood_type}</span>
                          </span>
                        </div>

                        <div className="p-2.5 rounded-lg bg-muted/40 border border-border/60">
                          <span className="text-[10px] uppercase font-bold text-muted-foreground block mb-0.5">
                            Component and units
                          </span>
                          <span className="text-sm font-black text-foreground flex items-center gap-1">
                            <span>{opp.component.replaceAll('_', ' ')}</span>
                            <span>· {opp.units_requested} {opp.units_requested === 1 ? 'unit' : 'units'}</span>
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between text-xs text-muted-foreground pt-1">
                        <div className="flex items-center gap-1.5 font-medium">
                          <span>📍</span>
                          <span>{opp.city}</span>
                        </div>
                        <span className="text-[11px]">
                          Compatible with Type {profile?.blood_type}
                        </span>
                      </div>

                      <div className="pt-2 border-t border-border/60 flex items-center justify-end">
                        <Link href={`/donor/opportunities/${opp.id}`} className="w-full sm:w-auto">
                          <Button variant="primary" size="sm" className="w-full font-bold text-xs shadow-sm">
                            View Emergency Details →
                          </Button>
                        </Link>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="border-border bg-card">
                <CardContent className="py-12 text-center space-y-2">
                  <div className="text-3xl">🕊️</div>
                  <h3 className="text-sm font-bold text-foreground">No compatible emergency blood requests are currently available.</h3>
                  <p className="text-sm text-muted-foreground max-w-md mx-auto">
                    Your profile has no compatible requests in the results currently available. Check this page again for updated results.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </>
      )}
    </div>
  );
}
