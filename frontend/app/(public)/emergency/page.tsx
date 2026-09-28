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
  const [step, setStep] = useState(1);

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

  const handleContinue = () => {
    setErrorMessage(null);
    if (step === 2 && patientAge && (Number(patientAge) < 1 || Number(patientAge) > 120)) {
      setErrorMessage('Enter an age from 1 to 120, or leave the field blank.');
      return;
    }
    if (!hospitalName.trim() || !city.trim()) {
      setErrorMessage('Enter the hospital or facility name and city to continue.');
      return;
    }
    if (patientName.trim() && /\d/.test(patientName)) {
      setErrorMessage('Patient identifier/name cannot contain numbers.');
      setStep(2);
      return;
    }
    setStep((current) => Math.min(3, current + 1));
  };

  return (
    <div className="py-10 sm:py-16">
      <div className="container mx-auto max-w-4xl px-4 sm:px-6">
        
        {/* Top Header */}
        <div className="mx-auto mb-8 max-w-2xl space-y-3 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-critical/30 bg-critical/10 px-3.5 py-1 text-xs font-semibold text-critical">
            <span className="h-2 w-2 rounded-full bg-critical animate-pulse" />
            <span>CLINICAL EMERGENCY INTAKE DESK</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-4xl">
            Request Emergency Blood
          </h1>
          <p className="mx-auto max-w-xl text-sm leading-6 text-muted-foreground sm:text-base">
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
                Track request status →
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Error Alert */}
        {errorMessage && (
          <div className="mb-6 rounded-xl border border-critical/40 bg-critical/10 p-4 text-sm font-medium text-critical" role="alert" aria-live="assertive">
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
            <ol aria-label="Emergency request steps" className="mb-6 grid grid-cols-3 gap-2">
              {['Request details', 'Optional details', 'Review'].map((label, index) => {
                const number = index + 1;
                const current = step === number;
                return (
                  <li key={label} aria-current={current ? 'step' : undefined} className={`border-b-2 pb-2 text-xs sm:text-sm ${current ? 'border-primary font-semibold text-primary' : step > number ? 'border-success text-foreground' : 'border-border text-muted-foreground'}`}>
                    <span className="mr-1.5">{step > number ? '✓' : number}</span>{label}
                  </li>
                );
              })}
            </ol>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div hidden={step !== 1} className="space-y-6">
              
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

              </div>

              <div hidden={step !== 2} className="space-y-6">
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

              </div>

              {step === 3 && (
                <section aria-labelledby="review-request-heading" className="space-y-4 rounded-xl border border-border bg-muted/40 p-4 sm:p-5">
                  <h3 id="review-request-heading" className="text-base font-semibold">Review request details</h3>
                  <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
                    <div><dt className="text-muted-foreground">Blood group</dt><dd className="font-semibold">{bloodType}</dd></div>
                    <div><dt className="text-muted-foreground">Units required</dt><dd className="font-semibold">{unitsRequired}</dd></div>
                    <div><dt className="text-muted-foreground">Urgency</dt><dd className="font-semibold">{urgencyLevel}</dd></div>
                    <div><dt className="text-muted-foreground">Hospital / facility</dt><dd className="font-semibold">{hospitalName}</dd></div>
                    <div><dt className="text-muted-foreground">City</dt><dd className="font-semibold">{city}</dd></div>
                    <div><dt className="text-muted-foreground">Patient details</dt><dd className="font-semibold">{patientName || 'Not provided'}{patientAge ? ` · age ${patientAge}` : ''}</dd></div>
                    {notes && <div className="sm:col-span-2"><dt className="text-muted-foreground">Clinical notes</dt><dd className="break-words font-semibold">{notes}</dd></div>}
                  </dl>
                  <p className="text-xs leading-5 text-muted-foreground">Only provide details required to coordinate this request. Patient details are submitted to the service and are not shown in public tracking.</p>
                </section>
              )}

              <div className="sticky bottom-0 -mx-4 flex gap-3 border-t border-border bg-card/95 px-4 py-3 backdrop-blur sm:static sm:mx-0 sm:border-0 sm:bg-transparent sm:p-0">
                {step > 1 && <Button type="button" variant="outline" size="lg" className="flex-1 sm:flex-none" onClick={() => { setErrorMessage(null); setStep((current) => current - 1); }}>Back</Button>}
                {step < 3 ? (
                  <Button type="button" variant="primary" size="lg" className="flex-1 sm:flex-none" onClick={handleContinue}>Continue</Button>
                ) : (
                  <Button type="submit" variant="danger" size="lg" className="flex-1 font-semibold text-base sm:flex-none" isLoading={isSubmitting}>
                    Submit emergency request
                  </Button>
                )}
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
