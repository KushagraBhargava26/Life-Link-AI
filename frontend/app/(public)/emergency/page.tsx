'use client';

// frontend/app/(public)/emergency/page.tsx
// LifeLink AI — Emergency Request Intake
// Architecture Reference: ARCHITECTURE.md Section 17 & Section 30

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { emergencyService } from '@/services/emergencyService';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

function EmergencyIntakeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [bloodType, setBloodType] = useState<string>('O-');
  const [unitsRequired, setUnitsRequired] = useState<number>(2);
  const [urgencyLevel, setUrgencyLevel] = useState<string>('CRITICAL');
  const [hospitalName, setHospitalName] = useState<string>('');
  const [city, setCity] = useState<string>('Mumbai');
  const [patientName, setPatientName] = useState<string>('');
  const [patientAge, setPatientAge] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [trackNumberInput, setTrackNumberInput] = useState<string>('');

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const qBlood = searchParams.get('blood_type');
    if (qBlood) setBloodType(qBlood);
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage(null);

    if (!bloodType) {
      setErrorMessage('Blood group is required.');
      setIsSubmitting(false);
      return;
    }

    if (!hospitalName.trim()) {
      setErrorMessage('Hospital / Facility name is required.');
      setIsSubmitting(false);
      return;
    }

    if (!city.trim()) {
      setErrorMessage('City location is required.');
      setIsSubmitting(false);
      return;
    }

    if (patientName.trim() && /\d/.test(patientName)) {
      setErrorMessage('Patient identifier/name cannot contain numbers.');
      setIsSubmitting(false);
      return;
    }

    try {
      const response = await emergencyService.createRequest({
        blood_type: bloodType,
        units_required: Number(unitsRequired),
        urgency_level: urgencyLevel,
        hospital_name: hospitalName.trim(),
        city: city.trim(),
        patient_name: patientName.trim() || undefined,
        patient_age: patientAge ? Number(patientAge) : undefined,
        notes: notes.trim() || undefined,
      });

      if (response.success && response.data) {
        const reqNum = response.data.request_number;
        router.push(`/emergency/track/${encodeURIComponent(reqNum)}`);
      } else {
        setErrorMessage(response.message || 'Failed to create emergency requisition.');
      }
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || err.message || 'Network error during submission.';
      setErrorMessage(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTrackLookup = (e: React.FormEvent) => {
    e.preventDefault();
    if (trackNumberInput.trim()) {
      router.push(`/emergency/track/${encodeURIComponent(trackNumberInput.trim())}`);
    }
  };

  return (
    <div className="py-10 sm:py-16">
      <div className="container mx-auto max-w-4xl px-4 sm:px-6">
        
        {/* Top Header */}
        <div className="text-center max-w-2xl mx-auto mb-8 space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full border border-critical/30 bg-critical/10 px-3.5 py-1 text-xs font-bold text-critical">
            <span className="h-2 w-2 rounded-full bg-critical animate-pulse" />
            <span>CLINICAL EMERGENCY INTAKE DESK</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
            Request Emergency Blood
          </h1>
          <p className="text-sm text-muted-foreground">
            Zero-barrier submission for attending physicians, trauma teams, and family members. No account required.
          </p>
        </div>

        {/* Existing Request Lookup Bar */}
        <Card className="mb-8 border-border bg-card-elevated shadow-sm">
          <CardContent className="p-4">
            <form onSubmit={handleTrackLookup} className="flex flex-col sm:flex-row items-center gap-3">
              <div className="flex-1 w-full">
                <Input
                  label="Track Existing Requisition"
                  placeholder="Enter Requisition Code (e.g. EMR-2026-0001)"
                  value={trackNumberInput}
                  onChange={(e) => setTrackNumberInput(e.target.value)}
                  className="font-mono uppercase"
                  required
                />
              </div>
              <Button type="submit" variant="secondary" size="md" className="w-full sm:w-auto sm:self-end h-10 font-semibold shrink-0 text-xs">
                Track Live Status →
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Error Alert */}
        {errorMessage && (
          <div className="mb-8 rounded-xl border border-critical/40 bg-critical/10 p-4 text-sm font-medium text-critical" role="alert">
            {errorMessage}
          </div>
        )}

        {/* Main Intake Form */}
        <Card className="border-border shadow-lg bg-card">
          <CardHeader className="border-b border-border/60 pb-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl">Emergency Requisition Details</CardTitle>
                <CardDescription>
                  Provide accurate clinical requirements.
                </CardDescription>
              </div>
              <span className="text-xs text-muted-foreground">
                <span className="text-destructive font-bold">*</span> Required field
              </span>
            </div>
          </CardHeader>

          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              
              {/* Blood Group Selector */}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                  Required Blood Group &amp; Rh Factor <span className="text-destructive">*</span>
                </label>
                <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
                  {['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'].map((bg) => {
                    const isSelected = bloodType === bg;
                    return (
                      <button
                        key={bg}
                        type="button"
                        onClick={() => setBloodType(bg)}
                        className={`h-12 rounded-lg font-bold text-sm transition-all border ${
                          isSelected
                            ? 'bg-primary text-primary-foreground border-primary shadow-sm scale-105'
                            : 'bg-card text-foreground border-border hover:border-primary/50 hover:bg-muted'
                        } focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring`}
                        aria-pressed={isSelected}
                      >
                        {bg}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Units & Urgency */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="units-select" className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                    Units Required (1-20) <span className="text-destructive">*</span>
                  </label>
                  <select
                    id="units-select"
                    value={unitsRequired}
                    onChange={(e) => setUnitsRequired(Number(e.target.value))}
                    className="w-full h-10 rounded-lg border border-border bg-card px-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    required
                  >
                    {[1, 2, 3, 4, 5, 6, 8, 10, 15, 20].map((u) => (
                      <option key={u} value={u}>
                        {u} {u === 1 ? 'Unit (450 ml)' : 'Units'}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="urgency-select" className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                    Clinical Urgency Level <span className="text-destructive">*</span>
                  </label>
                  <select
                    id="urgency-select"
                    value={urgencyLevel}
                    onChange={(e) => setUrgencyLevel(e.target.value)}
                    className="w-full h-10 rounded-lg border border-border bg-card px-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    required
                  >
                    <option value="CRITICAL">🚨 Critical (Immediate Transfusion / Trauma)</option>
                    <option value="HIGH">⚠️ High (Within 2 Hours)</option>
                    <option value="MEDIUM">⏳ Medium (Within 6 Hours)</option>
                    <option value="LOW">📅 Routine (Scheduled Surgery)</option>
                  </select>
                </div>
              </div>

              {/* Destination Facility & City */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                    Hospital / Medical Facility <span className="text-destructive">*</span>
                  </label>
                  <Input
                    placeholder="e.g. Lilavati Hospital & Research Centre"
                    value={hospitalName}
                    onChange={(e) => setHospitalName(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                    City Location <span className="text-destructive">*</span>
                  </label>
                  <Input
                    placeholder="e.g. Mumbai, Bengaluru, Delhi"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* Patient Details (Protected) */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Patient Identifier or Name (Optional)"
                  placeholder="e.g. Priya Sharma"
                  value={patientName}
                  onChange={(e) => setPatientName(e.target.value)}
                  helperText="Protected by DPDP privacy shield. Never exposed publicly."
                />
                <Input
                  label="Patient Age (Optional)"
                  type="number"
                  min="1"
                  max="120"
                  placeholder="e.g. 34"
                  value={patientAge}
                  onChange={(e) => setPatientAge(e.target.value)}
                />
              </div>

              {/* Clinical Notes */}
              <div>
                <label htmlFor="clinical-notes" className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                  Clinical Notes / Department (Optional)
                </label>
                <textarea
                  id="clinical-notes"
                  rows={3}
                  placeholder="e.g. ICU Bed 4, severe trauma surgery scheduled at 14:00. Attending Dr. Roy."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full rounded-lg border border-border bg-card p-3 text-sm text-foreground placeholder:text-muted-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>

              <div className="pt-2">
                <Button
                  type="submit"
                  variant="danger"
                  size="lg"
                  className="w-full font-bold shadow-lg shadow-critical/20 text-base"
                  isLoading={isSubmitting}
                >
                  <span>🚨 Broadcast Emergency Request</span>
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}

export default function EmergencyIntakePage() {
  return (
    <Suspense
      fallback={
        <div className="py-20 flex flex-col items-center justify-center space-y-3">
          <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          <span className="text-sm text-muted-foreground">Loading Emergency Intake Desk...</span>
        </div>
      }
    >
      <EmergencyIntakeContent />
    </Suspense>
  );
}
