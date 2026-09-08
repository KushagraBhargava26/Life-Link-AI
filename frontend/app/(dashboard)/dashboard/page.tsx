'use client';

// frontend/app/(dashboard)/dashboard/page.tsx
// LifeLink AI — Smart Role Portal Router & Account Hub
// Architecture Reference: ARCHITECTURE.md Section 15 & Section 18

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { authService } from '@/services/authService';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { getDefaultDashboardPath, getPrimaryRole, isHospitalStaff, isBloodBankStaff, isDonor, isAdmin } from '@/lib/auth';

export default function DashboardPage() {
  const router = useRouter();
  const { user, clearAuth } = useAuthStore();

  useEffect(() => {
    if (user) {
      const defaultPath = getDefaultDashboardPath(user);
      if (defaultPath !== '/dashboard') {
        router.replace(defaultPath);
      }
    }
  }, [user, router]);

  const handleLogout = async () => {
    try {
      await authService.logout();
    } catch (e) {
      // ignore
    } finally {
      clearAuth();
      router.push('/');
    }
  };

  const primaryRole = getPrimaryRole(user);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-green-500/30 bg-green-500/10 px-3 py-1 text-xs font-semibold text-green-600 dark:text-green-400 mb-2">
            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            <span>Authenticated Session Verified</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            Welcome, {user?.first_name || 'Member'} {user?.last_name || ''}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Registered Email: <span className="text-foreground font-mono">{user?.email}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" size="md" onClick={handleLogout}>
            Sign Out
          </Button>
        </div>
      </div>

      {/* Role Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {isDonor(primaryRole) && (
          <Card className="border-border shadow-sm bg-card hover:border-primary/50 transition-colors">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <span>🩸</span> Donor Portal
              </CardTitle>
              <CardDescription>
                Manage emergency availability, check cooldown eligibility, and view compatible requisitions.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/donor">
                <Button variant="primary" size="sm" className="w-full font-semibold">
                  Open Donor Dashboard →
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {isHospitalStaff(primaryRole) && (
          <Card className="border-border shadow-sm bg-card hover:border-primary/50 transition-colors">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <span>🏥</span> Hospital Trauma Portal
              </CardTitle>
              <CardDescription>
                Submit emergency requisitions, coordinate matching runs, and monitor candidate responses.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Link href="/hospital">
                <Button variant="secondary" size="sm" className="w-full font-semibold">
                  Open Hospital Portal →
                </Button>
              </Link>
              <Link href="/hospital/requests">
                <Button variant="ghost" size="sm" className="w-full">
                  View Requisitions
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {isBloodBankStaff(primaryRole) && (
          <Card className="border-border shadow-sm bg-card hover:border-primary/50 transition-colors">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <span>🩸</span> Blood Bank Console
              </CardTitle>
              <CardDescription>
                Manage blood inventory by group and component, update stock, and monitor regional demand.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/blood-bank">
                <Button variant="secondary" size="sm" className="w-full font-semibold">
                  Open Blood Bank Console →
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {/* Account Details Card */}
        <Card className="border-border shadow-sm bg-card">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <span>🛡️</span> Account Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="flex flex-wrap gap-2">
              {user?.roles && user.roles.length > 0 ? (
                user.roles.map((r) => (
                  <Badge key={r} variant="default">
                    {r}
                  </Badge>
                ))
              ) : (
                <Badge variant="default">{user?.role || 'DONOR'}</Badge>
              )}
            </div>
            <div className="text-muted-foreground space-y-1 pt-2 border-t border-border/60">
              <p>Account Status: <strong className="text-green-600 dark:text-green-400">Active</strong></p>
              <p>Primary Role: <span className="text-foreground font-semibold">{primaryRole}</span></p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
