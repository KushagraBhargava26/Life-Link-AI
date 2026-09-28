// frontend/app/(public)/layout.tsx
// LifeLink AI — Standard Public Layout
// Architecture Reference: ARCHITECTURE.md Section 15

import React from 'react';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground transition-colors">
      <a href="#main-content" className="sr-only z-50 rounded-md bg-card px-4 py-3 text-foreground focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:ring-2 focus:ring-ring">
        Skip to main content
      </a>
      <Navbar />
      <main id="main-content" tabIndex={-1} className="min-w-0 flex-1">{children}</main>
      <Footer />
    </div>
  );
}
