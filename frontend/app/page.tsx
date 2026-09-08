'use client';

// frontend/app/page.tsx
// LifeLink AI — Professional Healthcare Emergency Coordination Platform
// Architecture Reference: ARCHITECTURE.md Section 15

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

// Blood Compatibility Matrix & Facts
const BLOOD_FACTS: Record<string, { giveTo: string; receiveFrom: string; note: string; rarity: string }> = {
  'O-': {
    giveTo: 'All Blood Types (Universal Donor)',
    receiveFrom: 'O- only',
    note: 'Crucial for trauma emergencies when patient blood type is unknown.',
    rarity: 'Universal Donor for Red Blood Cells',
  },
  'O+': {
    giveTo: 'O+, A+, B+, AB+',
    receiveFrom: 'O+, O-',
    note: 'Most common and most frequently transfused blood type.',
    rarity: 'High clinical demand across trauma centers',
  },
  'A-': {
    giveTo: 'A-, A+, AB-, AB+',
    receiveFrom: 'A-, O-',
    note: 'Vital for oncology and scheduled surgical procedures.',
    rarity: 'Compatible with A-, A+, AB-, AB+',
  },
  'A+': {
    giveTo: 'A+, AB+',
    receiveFrom: 'A+, A-, O+, O-',
    note: 'High demand for platelets and whole blood.',
    rarity: 'Second most common blood type',
  },
  'B-': {
    giveTo: 'B-, B+, AB-, AB+',
    receiveFrom: 'B-, O-',
    note: 'Critical for emergency reserves in regional blood banks.',
    rarity: 'High priority during multi-trauma incidents',
  },
  'B+': {
    giveTo: 'B+, AB+',
    receiveFrom: 'B+, B-, O+, O-',
    note: 'High clinical requirement across emergency wards.',
    rarity: 'Widely needed across South Asian healthcare systems',
  },
  'AB-': {
    giveTo: 'AB-, AB+',
    receiveFrom: 'All Negative Types (O-, A-, B-, AB-)',
    note: 'Universal platelet donor — highly valued for ICU and trauma care.',
    rarity: 'Universal Platelet Donor',
  },
  'AB+': {
    giveTo: 'AB+ only',
    receiveFrom: 'All Blood Types (Universal Recipient)',
    note: 'Universal plasma donor for severe burn and massive trauma resuscitation.',
    rarity: 'Universal Plasma Donor',
  },
};

export default function HomePage() {
  const router = useRouter();
  const [selectedBlood, setSelectedBlood] = useState<string>('O-');
  const [trackingId, setTrackingId] = useState<string>('');

  const handleTrack = (e: React.FormEvent) => {
    e.preventDefault();
    if (trackingId.trim()) {
      router.push(`/emergency/track/${encodeURIComponent(trackingId.trim())}`);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground transition-colors">
      <Navbar />

      <main className="flex-1">
        {/* Semantic Emergency Protocol Bar */}
        <section className="border-b border-critical/20 bg-critical/5 px-4 py-2.5 transition-colors">
          <div className="container mx-auto flex max-w-7xl items-center justify-between text-xs sm:text-sm">
            <div className="flex items-center gap-2">
              <span className="flex h-2 w-2 rounded-full bg-critical animate-pulse" aria-hidden="true" />
              <strong className="font-semibold text-critical">Emergency Coordination Protocol:</strong>
              <span className="text-muted-foreground hidden sm:inline">
                Real-time deterministic matching active for trauma centers and blood banks.
              </span>
              <span className="text-muted-foreground sm:hidden">
                Emergency blood coordination active.
              </span>
            </div>
            <Link
              href="/emergency"
              className="font-semibold text-critical hover:underline underline-offset-2 flex items-center gap-1 shrink-0"
            >
              <span>Emergency Intake Desk</span>
              <span aria-hidden="true">→</span>
            </Link>
          </div>
        </section>

        {/* Hero Section */}
        <section className="relative overflow-hidden py-12 sm:py-16 lg:py-20 border-b border-border/60">
          <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
              
              {/* Hero Left Column */}
              <div className="lg:col-span-7 space-y-6 text-left">
                <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3.5 py-1 text-xs font-semibold text-primary">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                  <span>EMERGENCY BLOOD COORDINATION</span>
                </div>

                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-foreground leading-[1.1]">
                  When Blood Is Needed,{' '}
                  <span className="text-primary underline decoration-primary/30 underline-offset-8">
                    Every Second
                  </span>{' '}
                  Matters.
                </h1>

                <p className="text-base sm:text-lg text-muted-foreground leading-relaxed max-w-2xl">
                  LifeLink AI connects hospitals with compatible blood-bank inventory and eligible donors through a privacy-conscious emergency coordination workflow.
                </p>

                {/* Central Prominent Balanced CTA Card */}
                <div className="p-6 rounded-2xl border border-border bg-card shadow-lg max-w-xl space-y-4">
                  <div className="flex items-center justify-between border-b border-border/60 pb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">🩸</span>
                      <div>
                        <h2 className="text-sm font-bold text-foreground">Healthcare &amp; Donor Access</h2>
                        <p className="text-xs text-muted-foreground">Sign in to your dashboard or create a new account</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-[10px] font-bold">Secure Portal</Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-1">
                    <Link href="/login" className="w-full">
                      <Button variant="outline" size="lg" className="w-full font-bold text-sm h-12 shadow-sm">
                        Sign In
                      </Button>
                    </Link>
                    <Link href="/register" className="w-full">
                      <Button variant="primary" size="lg" className="w-full font-bold text-sm h-12 shadow-md shadow-primary/20">
                        Register Account
                      </Button>
                    </Link>
                  </div>
                </div>

                {/* Value Propositions */}
                <div className="pt-4 grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
                  <div className="p-3 rounded-lg bg-card border border-border">
                    <div className="text-xs font-bold text-foreground">Emergency Requests</div>
                    <div className="text-[11px] text-muted-foreground mt-0.5">Rapid trauma intake with live tracking</div>
                  </div>
                  <div className="p-3 rounded-lg bg-card border border-border">
                    <div className="text-xs font-bold text-foreground">Compatible Blood</div>
                    <div className="text-[11px] text-muted-foreground mt-0.5">Deterministic ABO/Rh standard</div>
                  </div>
                  <div className="p-3 rounded-lg bg-card border border-border">
                    <div className="text-xs font-bold text-foreground">Faster Coordination</div>
                    <div className="text-[11px] text-muted-foreground mt-0.5">Direct connection to banks &amp; donors</div>
                  </div>
                </div>
              </div>

              {/* Hero Right Column: Emergency Intake & Tracking Desk */}
              <div className="lg:col-span-5">
                <Card className="border-border shadow-xl bg-card transition-all">
                  <CardHeader className="pb-3 border-b border-border/60">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="flex h-2.5 w-2.5 rounded-full bg-critical animate-pulse" />
                        <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                          Emergency Blood Desk
                        </span>
                      </div>
                      <Badge variant="critical">24/7 Intake</Badge>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-5 pt-4 text-xs">
                    <div className="space-y-2">
                      <h3 className="text-sm font-bold text-foreground">Immediate Emergency Requisition</h3>
                      <p className="text-muted-foreground">
                        Need blood urgently for a patient or surgical emergency? Create an emergency requisition without an account.
                      </p>
                      <Link href="/emergency" className="block pt-1">
                        <Button variant="danger" size="md" className="w-full font-bold shadow-sm">
                          <span>🚨 Create Emergency Request</span>
                        </Button>
                      </Link>
                    </div>

                    <div className="border-t border-border/60 pt-4 space-y-3">
                      <h3 className="text-sm font-bold text-foreground">Track Existing Requisition</h3>
                      <p className="text-muted-foreground">
                        Enter your emergency tracking code (e.g. EMR-2026-XXXX) to view live fulfillment status.
                      </p>
                      <form onSubmit={handleTrack} className="flex gap-2">
                        <Input
                          type="text"
                          placeholder="Enter Tracking Code..."
                          value={trackingId}
                          onChange={(e) => setTrackingId(e.target.value)}
                          className="text-xs font-mono"
                        />
                        <Button type="submit" variant="secondary" size="md" className="shrink-0 font-semibold">
                          Track
                        </Button>
                      </form>
                    </div>

                    <div className="border-t border-border/60 pt-4 flex items-center justify-between text-[11px] text-muted-foreground">
                      <span>Attending clinician or blood bank custodian?</span>
                      <Link href="/login" className="font-semibold text-primary hover:underline">
                        Portal Login →
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              </div>

            </div>
          </div>
        </section>

        {/* Interactive Blood Group Compatibility Explorer */}
        <section className="py-14 bg-muted/30 border-b border-border/60 transition-colors">
          <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-8 space-y-2">
              <Badge variant="outline" className="text-xs uppercase tracking-wider font-bold">Clinical Reference</Badge>
              <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                Blood Group Transfusion Standards
              </h2>
              <p className="text-sm text-muted-foreground">
                Select any blood group to inspect universal transfusion compatibility standards and clinical profile.
              </p>
            </div>

            {/* 8-Button Selector */}
            <div className="flex flex-wrap items-center justify-center gap-2.5 sm:gap-3 max-w-3xl mx-auto mb-8">
              {['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'].map((bg) => {
                const isSelected = selectedBlood === bg;
                return (
                  <button
                    key={bg}
                    type="button"
                    onClick={() => setSelectedBlood(bg)}
                    className={`h-12 w-16 sm:h-14 sm:w-20 rounded-xl font-extrabold text-base sm:text-lg transition-all border ${
                    isSelected
                      ? 'bg-primary text-primary-foreground border-primary shadow-md shadow-primary/20 scale-105'
                      : 'bg-card text-foreground border-border hover:border-primary/50 hover:bg-muted'
                  } focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring`}
                    aria-pressed={isSelected}
                  >
                    {bg}
                  </button>
                );
              })}
            </div>

            {/* Dynamic Blood Details Card */}
            {selectedBlood && BLOOD_FACTS[selectedBlood] && (
              <div className="max-w-3xl mx-auto rounded-xl border border-border bg-card p-6 shadow-sm animate-fade-in">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/60 pb-4 mb-4">
                  <div className="flex items-center gap-3">
                    <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary font-black text-2xl">
                      {selectedBlood}
                    </span>
                    <div>
                      <h3 className="text-lg font-bold text-foreground">
                        Type {selectedBlood} Clinical Profile
                      </h3>
                      <p className="text-xs text-muted-foreground">
                        {BLOOD_FACTS[selectedBlood].rarity}
                      </p>
                    </div>
                  </div>
                  <Link href={`/emergency?blood_type=${encodeURIComponent(selectedBlood)}`}>
                    <Button variant="outline" size="sm" className="font-semibold text-xs">
                      <span>🚨 Request Type {selectedBlood}</span>
                    </Button>
                  </Link>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div className="p-3.5 rounded-lg bg-muted/50 border border-border/60 space-y-1">
                    <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider block">
                      Can Transfuse Red Blood Cells To:
                    </span>
                    <p className="text-foreground font-semibold text-sm">
                      {BLOOD_FACTS[selectedBlood].giveTo}
                    </p>
                  </div>
                  <div className="p-3.5 rounded-lg bg-muted/50 border border-border/60 space-y-1">
                    <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider block">
                      Can Safely Receive RBC From:
                    </span>
                    <p className="text-foreground font-semibold text-sm">
                      {BLOOD_FACTS[selectedBlood].receiveFrom}
                    </p>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-border/60 text-xs text-muted-foreground flex items-center gap-2">
                  <span className="text-sm">ℹ️</span>
                  <span>{BLOOD_FACTS[selectedBlood].note}</span>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Dedicated Operational Portals Section */}
        <section className="py-14 border-b border-border/60">
          <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-8">
            <div className="text-center space-y-2 max-w-2xl mx-auto">
              <Badge variant="outline" className="text-xs uppercase tracking-wider font-bold">Role-Based Portals</Badge>
              <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                Workspaces for Healthcare Stakeholders
              </h2>
              <p className="text-sm text-muted-foreground">
                Tailored workflows engineered specifically for trauma centers, blood bank custodians, and voluntary donors.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Hospital Card */}
              <div className="p-6 rounded-xl border border-border bg-card space-y-4 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">🏥</span>
                    <h3 className="font-bold text-base text-foreground">Hospitals &amp; Trauma Desks</h3>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Create emergency requisitions, view facility operational verification status, trigger multi-source matching runs, and coordinate candidate response.
                  </p>
                </div>
                <div className="pt-2">
                  <Link href="/hospital" className="w-full block">
                    <Button variant="outline" size="sm" className="w-full text-xs font-semibold">
                      Hospital Portal →
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Blood Bank Card */}
              <div className="p-6 rounded-xl border border-border bg-card space-y-4 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">🩸</span>
                    <h3 className="font-bold text-base text-foreground">Licensed Blood Banks</h3>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Manage real-time inventory across blood groups and components, track collection and expiration dates, and monitor regional emergency demand feeds.
                  </p>
                </div>
                <div className="pt-2">
                  <Link href="/blood-bank" className="w-full block">
                    <Button variant="outline" size="sm" className="w-full text-xs font-semibold">
                      Blood Bank Console →
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Donor Card */}
              <div className="p-6 rounded-xl border border-border bg-card space-y-4 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">🤝</span>
                    <h3 className="font-bold text-base text-foreground">Voluntary Donors</h3>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Control emergency availability with an instant toggle, verify donation eligibility with automated 56-day cooldown timers, and view local compatible requisitions.
                  </p>
                </div>
                <div className="pt-2">
                  <Link href="/donor" className="w-full block">
                    <Button variant="outline" size="sm" className="w-full text-xs font-semibold">
                      Donor Dashboard →
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Learn More & Architecture CTA */}
        <section className="py-14 bg-muted/20">
          <div className="container mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center space-y-5">
            <h2 className="text-2xl sm:text-3xl font-black text-foreground tracking-tight">
              Learn More About LifeLink AI
            </h2>
            <p className="text-sm text-muted-foreground max-w-xl mx-auto">
              Read our full architectural breakdown, 3-step clinical workflow, AI decision-support principles, and DPDP privacy protections on our About page.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
              <Link href="/about">
                <Button variant="primary" size="lg" className="font-semibold">
                  <span>Explore Platform &amp; Architecture →</span>
                </Button>
              </Link>
              <Link href="/emergency">
                <Button variant="danger" size="lg" className="font-bold">
                  <span>🚨 Emergency Blood Request</span>
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
