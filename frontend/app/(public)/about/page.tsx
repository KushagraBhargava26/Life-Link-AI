'use client';

// frontend/app/(public)/about/page.tsx
// LifeLink AI — About Platform, Architecture & Clinical Workflow
// Architecture Reference: ARCHITECTURE.md Sections 1-10

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';

export default function AboutPage() {
  return (
    <div className="space-y-0">
      {/* Hero Section */}
        <section className="relative overflow-hidden border-b border-border/60 py-16 sm:py-24 bg-gradient-to-b from-muted/40 to-background">
          <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-semibold text-primary">
              <span>PLATFORM ARCHITECTURE &amp; MISSION</span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-foreground leading-tight">
              Rapid, Deterministic Emergency Blood Coordination
            </h1>

            <p className="text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              LifeLink AI is an open, standards-compliant digital infrastructure connecting hospital trauma units, licensed blood banks, and verified voluntary donors to eliminate emergency search latency during critical care windows.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <Link href="/emergency">
                <Button variant="danger" size="lg" className="font-bold shadow-md shadow-critical/20">
                  <span>🚨 Emergency Request Desk</span>
                </Button>
              </Link>
              <Link href="/register">
                <Button variant="secondary" size="lg" className="font-semibold">
                  <span>🩸 Register as Donor</span>
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* The Problem Statement */}
        <section className="py-16 border-b border-border/60">
          <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
              <div className="md:col-span-5 space-y-4">
                <Badge variant="outline" className="text-xs uppercase tracking-wider font-bold">The Challenge</Badge>
                <h2 className="text-3xl font-extrabold text-foreground tracking-tight">
                  The Golden Hour Emergency Bottleneck
                </h2>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  In acute trauma, severe hemorrhage, and surgical emergencies, patient survival hinges on obtaining compatible blood products within minutes.
                </p>
              </div>
              <div className="md:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Card className="border-border bg-card">
                  <CardContent className="pt-6 space-y-2">
                    <div className="text-xl">📞</div>
                    <h3 className="text-sm font-bold text-foreground">Fragmented Communication</h3>
                    <p className="text-xs text-muted-foreground">
                      Trauma coordinators frequently rely on manual phone calls to nearby facilities, wasting precious minutes during critical resuscitation.
                    </p>
                  </CardContent>
                </Card>
                <Card className="border-border bg-card">
                  <CardContent className="pt-6 space-y-2">
                    <div className="text-xl">📦</div>
                    <h3 className="text-sm font-bold text-foreground">Siloed Inventory</h3>
                    <p className="text-xs text-muted-foreground">
                      Blood banks maintain disconnected stock logs, leading to preventable shortages in one center while compatible units expire in another.
                    </p>
                  </CardContent>
                </Card>
                <Card className="border-border bg-card">
                  <CardContent className="pt-6 space-y-2">
                    <div className="text-xl">⏱️</div>
                    <h3 className="text-sm font-bold text-foreground">Donor Fatigue &amp; Delay</h3>
                    <p className="text-xs text-muted-foreground">
                      Uncoordinated broadcast appeals lead to spam, low response rates, and delayed dispatch of truly available, eligible donors.
                    </p>
                  </CardContent>
                </Card>
                <Card className="border-border bg-card">
                  <CardContent className="pt-6 space-y-2">
                    <div className="text-xl">🛡️</div>
                    <h3 className="text-sm font-bold text-foreground">Privacy Vulnerabilities</h3>
                    <p className="text-xs text-muted-foreground">
                      Social media broadcasts leak sensitive patient diagnostics and donor contact information across public channels.
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* 3-Step Clinical Workflow */}
        <section className="py-16 bg-muted/20 border-b border-border/60">
          <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 space-y-12">
            <div className="text-center space-y-3 max-w-2xl mx-auto">
              <Badge variant="outline" className="text-xs uppercase tracking-wider font-bold">Operational Pipeline</Badge>
              <h2 className="text-3xl font-black text-foreground tracking-tight">
                How LifeLink AI Coordinates in Real Time
              </h2>
              <p className="text-sm text-muted-foreground">
                A standardized three-stage lifecycle ensuring clinical rigor and zero ambiguity.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Step 1 */}
              <Card className="border-border bg-card relative">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary font-black text-sm">
                      01
                    </span>
                    <Badge variant="default">Intake</Badge>
                  </div>
                  <CardTitle className="text-base font-bold">Emergency Requisition</CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground space-y-2">
                  <p>
                    Hospital trauma staff or verified requesters submit an urgent requirement with required blood group, component (Whole Blood, RBC, Plasma), quantity, and clinical urgency.
                  </p>
                  <p className="font-medium text-foreground">
                    A unique tracking code is generated immediately for end-to-end visibility.
                  </p>
                </CardContent>
              </Card>

              {/* Step 2 */}
              <Card className="border-border bg-card relative">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary font-black text-sm">
                      02
                    </span>
                    <Badge variant="default">Matching</Badge>

                  </div>
                  <CardTitle className="text-base font-bold">Deterministic Discovery</CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground space-y-2">
                  <p>
                    The matching engine queries verified blood bank inventories and active eligible voluntary donors using deterministic ABO/Rh compatibility rules.
                  </p>
                  <p className="font-medium text-foreground">
                    Hospital coordinators review ranked candidates with complete explainability metrics.
                  </p>
                </CardContent>
              </Card>

              {/* Step 3 */}
              <Card className="border-border bg-card relative">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary font-black text-sm">
                      03
                    </span>
                    <Badge variant="success">Fulfillment</Badge>
                  </div>
                  <CardTitle className="text-base font-bold">Dispatch &amp; Custody</CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground space-y-2">
                  <p>
                    Targeted emergency alerts are dispatched to chosen blood banks or donors. Requisition status progresses in real-time until units are verified and received.
                  </p>
                  <p className="font-medium text-foreground">
                    Donor cooldown (56 days) is automatically logged to protect donor health.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Operational Portals & Roles */}
        <section className="py-16 border-b border-border/60">
          <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 space-y-10">
            <div className="text-center space-y-3 max-w-2xl mx-auto">
              <Badge variant="outline" className="text-xs uppercase tracking-wider font-bold">Stakeholder Network</Badge>
              <h2 className="text-3xl font-black text-foreground tracking-tight">
                Dedicated Role-Based Dashboards
              </h2>
              <p className="text-sm text-muted-foreground">
                Tailored interfaces designed specifically for clinical workflows, inventory custodians, and voluntary donors.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-6 rounded-xl border border-border bg-card space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🏥</span>
                  <h3 className="font-bold text-base text-foreground">Hospitals &amp; Trauma Desks</h3>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Create emergency requisitions, view facility operational verification status, trigger multi-source matching runs, and monitor candidate response in real-time.
                </p>
                <div className="pt-2">
                  <Link href="/hospital">
                    <Button variant="outline" size="sm" className="w-full text-xs font-semibold">
                      Hospital Portal
                    </Button>
                  </Link>
                </div>
              </div>

              <div className="p-6 rounded-xl border border-border bg-card space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🩸</span>
                  <h3 className="font-bold text-base text-foreground">Licensed Blood Banks</h3>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Manage real-time inventory across all 8 blood groups and components, track bag collection and expiration dates, and monitor regional emergency demand feeds.
                </p>
                <div className="pt-2">
                  <Link href="/blood-bank">
                    <Button variant="outline" size="sm" className="w-full text-xs font-semibold">
                      Blood Bank Console
                    </Button>
                  </Link>
                </div>
              </div>

              <div className="p-6 rounded-xl border border-border bg-card space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🤝</span>
                  <h3 className="font-bold text-base text-foreground">Voluntary Donors</h3>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Control personal emergency availability with a one-click toggle, verify eligibility with automated 56-day cooldown timers, and respond to local compatible requisitions.
                </p>
                <div className="pt-2">
                  <Link href="/donor">
                    <Button variant="outline" size="sm" className="w-full text-xs font-semibold">
                      Donor Dashboard
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* AI Transparency & Clinical Safety Principles */}
        <section className="py-16 bg-muted/20 border-b border-border/60">
          <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 space-y-8">
            <div className="max-w-3xl space-y-4">
              <Badge variant="outline" className="text-xs uppercase tracking-wider font-bold">Safety &amp; Compliance</Badge>
              <h2 className="text-3xl font-black text-foreground tracking-tight">
                Deterministic Medical Rules &amp; Explainable AI
              </h2>
              <p className="text-sm text-muted-foreground leading-relaxed">
                LifeLink AI upholds strict separation between deterministic medical rules and machine learning decision-support algorithms.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="p-5 rounded-xl border border-border bg-card space-y-2.5">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-primary" />
                  <h3 className="font-bold text-sm text-foreground">Deterministic Medical Compatibility</h3>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  ABO and Rh factor transfusion rules are pure, deterministic Python code with zero neural network ambiguity. A candidate is either medically compatible or strictly excluded.
                </p>
              </div>

              <div className="p-5 rounded-xl border border-border bg-card space-y-2.5">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-blue-500" />
                  <h3 className="font-bold text-sm text-foreground">Advisory Donor Propensity Scoring</h3>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Machine learning (trained on historical transfusion frequency, recency, and eligibility) is used exclusively to rank voluntary donors by response probability, minimizing dispatch latency.
                </p>
              </div>

              <div className="p-5 rounded-xl border border-border bg-card space-y-2.5">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-green-500" />
                  <h3 className="font-bold text-sm text-foreground">DPDP Act &amp; Privacy By Design</h3>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Patient clinical diagnosis and identity are never exposed to donors. Donor phone numbers and home addresses are never exposed to hospital portals; contact occurs via secure platform tokens.
                </p>
              </div>

              <div className="p-5 rounded-xl border border-border bg-card space-y-2.5">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-amber-500" />
                  <h3 className="font-bold text-sm text-foreground">Truthful Partner Verification</h3>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Hospital and blood bank facilities undergo license and registration verification. Verification state is honestly reflected across the platform to ensure trust.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16">
          <div className="container mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center space-y-6">
            <h2 className="text-3xl font-black text-foreground tracking-tight">
              Ready to Strengthen Emergency Preparedness?
            </h2>
            <p className="text-sm text-muted-foreground max-w-xl mx-auto">
              Join hospitals, licensed blood banks, and verified voluntary donors making emergency blood coordination fast, transparent, and dependable.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link href="/emergency">
                <Button variant="danger" size="lg" className="font-bold">
                  <span>🚨 Request Emergency Blood</span>
                </Button>
              </Link>
              <Link href="/register">
                <Button variant="primary" size="lg" className="font-semibold">
                  <span>🩸 Register as Voluntary Donor</span>
                </Button>
              </Link>
            </div>
          </div>
        </section>
    </div>
  );
}
