'use client';

// frontend/components/layout/Navbar.tsx
// LifeLink AI — Global Healthcare Navigation
// Architecture Reference: ARCHITECTURE.md Section 15

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { authService } from '@/services/authService';
import { Button } from '@/components/ui/Button';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { getPrimaryRole, isHospitalStaff, isBloodBankStaff, isDonor, isAdmin } from '@/lib/auth';

export function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, user, clearAuth } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLogout = async () => {
    try {
      await authService.logout();
    } catch (e) {
      // ignore
    } finally {
      clearAuth();
      setMobileMenuOpen(false);
      router.push('/');
    }
  };

  const primaryRole = getPrimaryRole(user);

  const isActive = (path: string) => {
    if (path === '/') return pathname === '/';
    return pathname.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/80 bg-background/95 backdrop-blur-md transition-colors">
      <div className="container mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        
        {/* Brand Logo & Left Nav Items */}
        <div className="flex items-center gap-6 sm:gap-8">
          <Link
            href="/"
            className="flex items-center gap-2.5 transition-opacity hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-lg py-1 px-1.5"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white shadow-sm shadow-primary/20">
              <span className="text-xl leading-none" aria-hidden="true">🩸</span>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="text-lg font-extrabold tracking-tight text-foreground">
                  LifeLink
                </span>
                <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-black uppercase tracking-wider text-primary">
                  AI
                </span>
              </div>
              <span className="text-[10px] font-medium tracking-wide text-muted-foreground uppercase -mt-1">
                Emergency Network
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium" aria-label="Main Navigation">
            {/* Common Links: Home -> About */}
            <Link
              href="/"
              className={`transition-colors hover:text-foreground ${
                pathname === '/' ? 'text-foreground font-semibold text-primary' : 'text-muted-foreground'
              }`}
            >
              Home
            </Link>
            <Link
              href="/about"
              className={`transition-colors hover:text-foreground ${
                isActive('/about') ? 'text-foreground font-semibold text-primary' : 'text-muted-foreground'
              }`}
            >
              About
            </Link>

            {/* Authenticated Role-Specific Links */}
            {mounted && isAuthenticated && (
              <>
                {isDonor(primaryRole) && (
                  <>
                    <Link
                      href="/donor"
                      className={`transition-colors hover:text-foreground flex items-center gap-1 ${
                        pathname === '/donor' ? 'text-primary font-semibold' : 'text-muted-foreground'
                      }`}
                    >
                      <span>Donor Dashboard</span>
                    </Link>
                    <Link
                      href="/dashboard"
                      className={`transition-colors hover:text-foreground ${
                        pathname === '/dashboard' ? 'text-primary font-semibold' : 'text-muted-foreground'
                      }`}
                    >
                      Profile
                    </Link>
                  </>
                )}

                {isHospitalStaff(primaryRole) && (
                  <>
                    <Link
                      href="/hospital"
                      className={`transition-colors hover:text-foreground ${
                        pathname === '/hospital' ? 'text-primary font-semibold' : 'text-muted-foreground'
                      }`}
                    >
                      Hospital Dashboard
                    </Link>
                    <Link
                      href="/hospital/requests"
                      className={`transition-colors hover:text-foreground ${
                        isActive('/hospital/requests') ? 'text-primary font-semibold' : 'text-muted-foreground'
                      }`}
                    >
                      Requisitions
                    </Link>
                    <Link
                      href="/hospital/profile"
                      className={`transition-colors hover:text-foreground ${
                        isActive('/hospital/profile') ? 'text-primary font-semibold' : 'text-muted-foreground'
                      }`}
                    >
                      Profile
                    </Link>
                  </>
                )}

                {isBloodBankStaff(primaryRole) && (
                  <>
                    <Link
                      href="/blood-bank"
                      className={`transition-colors hover:text-foreground ${
                        pathname === '/blood-bank' ? 'text-primary font-semibold' : 'text-muted-foreground'
                      }`}
                    >
                      Blood Bank
                    </Link>
                    <Link
                      href="/blood-bank"
                      className="text-muted-foreground hover:text-foreground transition-colors"
                    >
                      Inventory
                    </Link>
                    <Link
                      href="/blood-bank/profile"
                      className={`transition-colors hover:text-foreground ${
                        isActive('/blood-bank/profile') ? 'text-primary font-semibold' : 'text-muted-foreground'
                      }`}
                    >
                      Profile
                    </Link>
                  </>
                )}

                {isAdmin(primaryRole) && (
                  <Link
                    href="/admin"
                    className={`transition-colors hover:text-foreground ${
                      isActive('/admin') ? 'text-primary font-semibold' : 'text-muted-foreground'
                    }`}
                  >
                    Admin Dashboard
                  </Link>
                )}
              </>
            )}
          </nav>
        </div>

        {/* Desktop Right Actions: [Sign In] [Register] or [User Menu] [Sign Out] */}
        <div className="hidden md:flex items-center gap-3">
          <ThemeToggle />

          {mounted && isAuthenticated ? (
            <div className="flex items-center gap-2">
              <Link href="/dashboard">
                <Button variant="ghost" size="sm" className="font-medium text-xs">
                  <span>👤</span>
                  <span>{user?.first_name || 'Account'}</span>
                </Button>
              </Link>
              <Button variant="outline" size="sm" onClick={handleLogout} className="text-xs">
                Sign Out
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login">
                <Button variant="ghost" size="sm" className="font-medium text-xs">
                  Sign In
                </Button>
              </Link>
              <Link href="/register">
                <Button variant="primary" size="sm" className="font-medium text-xs shadow-sm">
                  Register
                </Button>
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Action & Hamburger Toggle */}
        <div className="flex items-center gap-2 md:hidden">
          <ThemeToggle />

          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle navigation menu"
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card text-foreground hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {mobileMenuOpen ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/>
              </svg>
            )}
          </button>
        </div>

      </div>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-border bg-card px-4 py-6 shadow-xl animate-slide-in">
          <nav className="flex flex-col space-y-3 text-base font-medium">
            <Link
              href="/"
              onClick={() => setMobileMenuOpen(false)}
              className="p-2 rounded-lg hover:bg-muted text-foreground transition-colors"
            >
              Home
            </Link>
            <Link
              href="/about"
              onClick={() => setMobileMenuOpen(false)}
              className="p-2 rounded-lg hover:bg-muted text-foreground transition-colors"
            >
              About
            </Link>

            {mounted && isAuthenticated ? (
              <div className="border-t border-border/60 pt-3 flex flex-col space-y-2">
                <div className="p-2 text-xs text-muted-foreground flex items-center justify-between">
                  <span>Signed in as:</span>
                  <strong className="text-foreground">{user?.email}</strong>
                </div>
                {isDonor(primaryRole) && (
                  <>
                    <Link href="/donor" onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="secondary" size="md" className="w-full justify-start font-semibold text-xs">
                        🩸 Donor Dashboard
                      </Button>
                    </Link>
                    <Link href="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" size="md" className="w-full justify-start text-xs">
                        👤 Donor Profile
                      </Button>
                    </Link>
                  </>
                )}
                {isHospitalStaff(primaryRole) && (
                  <>
                    <Link href="/hospital" onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="secondary" size="md" className="w-full justify-start font-semibold text-xs">
                        🏥 Hospital Dashboard
                      </Button>
                    </Link>
                    <Link href="/hospital/requests" onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="outline" size="md" className="w-full justify-start text-xs">
                        📋 Requisitions
                      </Button>
                    </Link>
                    <Link href="/hospital/profile" onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" size="md" className="w-full justify-start text-xs">
                        ⚙️ Hospital Profile
                      </Button>
                    </Link>
                  </>
                )}
                {isBloodBankStaff(primaryRole) && (
                  <>
                    <Link href="/blood-bank" onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="secondary" size="md" className="w-full justify-start font-semibold text-xs">
                        🩸 Blood Bank Dashboard
                      </Button>
                    </Link>
                    <Link href="/blood-bank/profile" onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" size="md" className="w-full justify-start text-xs">
                        ⚙️ Blood Bank Profile
                      </Button>
                    </Link>
                  </>
                )}
                {isAdmin(primaryRole) && (
                  <Link href="/admin" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="secondary" size="md" className="w-full justify-start font-semibold text-xs">
                      🛡️ Admin Dashboard
                    </Button>
                  </Link>
                )}
                <Button variant="outline" size="md" onClick={handleLogout} className="w-full text-xs mt-2">
                  Sign Out
                </Button>
              </div>
            ) : (
              <div className="border-t border-border/60 pt-4 grid grid-cols-2 gap-3">
                <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="outline" size="md" className="w-full text-xs">
                    Sign In
                  </Button>
                </Link>
                <Link href="/register" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="primary" size="md" className="w-full text-xs">
                    Register
                  </Button>
                </Link>
              </div>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
