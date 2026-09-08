'use client';

// frontend/components/layout/Footer.tsx
// LifeLink AI — Platform Healthcare Footer
// Architecture Reference: ARCHITECTURE.md Section 15

import React from 'react';
import Link from 'next/link';

export function Footer() {
  return (
    <footer className="border-t border-border bg-card/60 text-foreground transition-colors">
      <div className="container mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pb-8 border-b border-border/70">
          
          {/* Col 1: Platform Identity */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl" aria-hidden="true">🩸</span>
              <span className="text-lg font-bold tracking-tight">LifeLink AI</span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed max-w-sm">
              Rapid emergency blood coordination connecting hospital trauma centers, licensed blood banks, and voluntary donors with deterministic medical safety.
            </p>
            <div className="inline-flex items-center gap-1.5 rounded-full border border-green-500/30 bg-green-500/10 px-2.5 py-0.5 text-[11px] font-medium text-green-600 dark:text-green-400">
              <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
              <span>Platform Online • Coordination Active</span>
            </div>
          </div>

          {/* Col 2: Navigation Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">
              About Platform
            </h4>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li>
                <Link href="/" className="hover:text-primary transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-primary transition-colors">
                  About Platform
                </Link>
              </li>
              <li>
                <Link href="/login" className="hover:text-primary transition-colors">
                  Sign In
                </Link>
              </li>
              <li>
                <Link href="/register" className="hover:text-primary transition-colors">
                  Register
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Administrative Governance */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">
              Administrative
            </h4>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li>
                <Link
                  href="/admin/login"
                  className="inline-flex items-center gap-1.5 text-primary hover:underline font-semibold"
                >
                  <span>🛡️</span>
                  <span>Admin Portal</span>
                </Link>
              </li>
              <li className="text-[11px] text-muted-foreground/80 leading-relaxed">
                Institutional governance, facility certificate review &amp; audit controls.
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Row */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted-foreground">
          <p>
            &copy; {new Date().getFullYear()} LifeLink AI Emergency Coordination. All rights reserved.
          </p>

          <div className="flex items-center gap-6">
            <Link href="/" className="text-[11px] text-muted-foreground hover:text-foreground transition-colors">
              Home
            </Link>
            <Link href="/about" className="text-[11px] text-muted-foreground hover:text-foreground transition-colors">
              About Platform
            </Link>
            <Link href="/admin/login" className="text-[11px] text-primary hover:underline font-semibold">
              Admin Portal
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
