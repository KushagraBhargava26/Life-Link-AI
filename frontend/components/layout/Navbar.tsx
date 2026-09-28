'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { authService } from '@/services/authService';
import { Button } from '@/components/ui/Button';
import { ThemeToggle } from '@/components/ui/ThemeToggle';

const publicLinks = [
  { label: 'Home', href: '/' },
  { label: 'About', href: '/about' },
];

export function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, user, clearAuth } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);
  useEffect(() => setMobileMenuOpen(false), [pathname]);
  useEffect(() => {
    if (!mobileMenuOpen) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMobileMenuOpen(false);
    };
    window.addEventListener('keydown', closeOnEscape);
    return () => window.removeEventListener('keydown', closeOnEscape);
  }, [mobileMenuOpen]);

  const handleLogout = async () => {
    try {
      await authService.logout();
    } catch {
      // Clear the local session even if the network is unavailable.
    } finally {
      clearAuth();
      setMobileMenuOpen(false);
      router.push('/');
    }
  };

  const dashboardHref = '/dashboard';
  const menuId = 'primary-navigation-mobile';

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur-md">
      <div className="container mx-auto flex min-h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="flex min-h-11 shrink-0 items-center gap-2 rounded-lg px-1.5 py-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          aria-label="LifeLink AI home"
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-base font-bold text-primary-foreground" aria-hidden="true">LL</span>
          <span className="flex flex-col">
            <span className="flex items-center gap-1.5 text-lg font-extrabold leading-5 tracking-tight text-foreground">
              LifeLink <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-bold tracking-wide text-primary">AI</span>
            </span>
            <span className="text-[10px] font-medium leading-4 tracking-wide text-muted-foreground">Emergency coordination</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-5 text-sm font-medium lg:flex" aria-label="Primary navigation">
          {publicLinks.map((item) => {
            const active = item.href === '/' ? pathname === '/' : pathname.startsWith(item.href);
            return <Link key={item.href} href={item.href} aria-current={active ? 'page' : undefined} className={`rounded-md px-2 py-2 transition-colors hover:text-foreground ${active ? 'font-semibold text-primary' : 'text-muted-foreground'}`}>{item.label}</Link>;
          })}
          <Link href="/emergency" aria-current={pathname === '/emergency' ? 'page' : undefined} className="inline-flex min-h-11 items-center rounded-lg bg-primary px-4 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
            Emergency request
          </Link>
        </nav>

        <div className="hidden items-center gap-2 lg:flex">
          <ThemeToggle />
          {mounted && isAuthenticated ? (
            <>
              <Link href={dashboardHref} className="inline-flex min-h-11 max-w-44 items-center truncate rounded-lg px-3 text-sm font-medium text-foreground hover:bg-muted" title={user?.email || 'Account'}>
                {user?.first_name || 'My account'}
              </Link>
              <Button variant="outline" size="sm" onClick={handleLogout}>Sign out</Button>
            </>
          ) : (
            <>
              <Link href="/login" className="inline-flex min-h-11 items-center rounded-lg px-3 text-sm font-medium text-foreground hover:bg-muted">Sign in</Link>
              <Link href="/register" className="inline-flex min-h-11 items-center rounded-lg border border-border px-3 text-sm font-medium text-foreground hover:bg-muted">Create account</Link>
            </>
          )}
        </div>

        <div className="flex items-center gap-2 lg:hidden">
          <ThemeToggle />
          <button
            type="button"
            onClick={() => setMobileMenuOpen((open) => !open)}
            aria-expanded={mobileMenuOpen}
            aria-controls={menuId}
            aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            className="inline-flex h-11 w-11 items-center justify-center rounded-lg border border-border bg-card text-foreground hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {mobileMenuOpen ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><path d="m18 6-12 12M6 6l12 12" /></svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16" /></svg>
            )}
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <nav id={menuId} aria-label="Mobile navigation" className="border-t border-border bg-card px-4 py-4 shadow-lg lg:hidden sm:px-6">
          <div className="mx-auto flex max-w-7xl flex-col gap-1">
            {publicLinks.map((item) => (
              <Link key={item.href} href={item.href} aria-current={(item.href === '/' ? pathname === '/' : pathname.startsWith(item.href)) ? 'page' : undefined} className="flex min-h-11 items-center rounded-lg px-3 text-sm font-medium text-foreground hover:bg-muted">{item.label}</Link>
            ))}
            <Link href="/emergency" aria-current={pathname === '/emergency' ? 'page' : undefined} className="my-1 flex min-h-11 items-center rounded-lg bg-primary px-3 text-sm font-semibold text-primary-foreground">Emergency request</Link>
            {mounted && isAuthenticated ? (
              <>
                <div className="mt-2 border-t border-border px-3 pt-3 text-xs text-muted-foreground">Signed in as <span className="break-all font-medium text-foreground">{user?.email}</span></div>
                <Link href={dashboardHref} className="flex min-h-11 items-center rounded-lg px-3 text-sm font-medium text-foreground hover:bg-muted">Open my workspace</Link>
                <button type="button" onClick={handleLogout} className="flex min-h-11 items-center rounded-lg px-3 text-left text-sm font-medium text-foreground hover:bg-muted">Sign out</button>
              </>
            ) : (
              <div className="mt-2 grid grid-cols-2 gap-2 border-t border-border pt-3">
                <Link href="/login" className="flex min-h-11 items-center justify-center rounded-lg border border-border px-3 text-sm font-medium text-foreground">Sign in</Link>
                <Link href="/register" className="flex min-h-11 items-center justify-center rounded-lg bg-primary px-3 text-sm font-semibold text-primary-foreground">Create account</Link>
              </div>
            )}
          </div>
        </nav>
      )}
    </header>
  );
}
