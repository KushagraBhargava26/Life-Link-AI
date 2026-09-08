'use client';

// frontend/app/(public)/admin/login/page.tsx
// LifeLink AI — Admin Governance Portal Authentication & Demo Access
// Architecture Reference: ARCHITECTURE.md Section 18 & Section 22

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/authService';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { getDefaultDashboardPath } from '@/lib/auth';

interface DemoPersona {
  roleName: string;
  badge: string;
  email: string;
  pass: string;
  targetDashboard: string;
  description: string;
}

const DEMO_PERSONAS: DemoPersona[] = [
  {
    roleName: 'Demo Admin',
    badge: 'SUPER_ADMIN',
    email: 'admin@lifelink.ai',
    pass: 'Admin@12345',
    targetDashboard: '/admin',
    description: 'Governance console, facility verification review, suspend/block controls.',
  },
  {
    roleName: 'Demo Hospital',
    badge: 'HOSPITAL_ADMIN',
    email: 'hospital.admin@apollo.org',
    pass: 'Hospital@12345',
    targetDashboard: '/hospital',
    description: 'Apollo Hospital trauma center, emergency requisitions & matching engine.',
  },
  {
    roleName: 'Demo Blood Bank',
    badge: 'BLOOD_BANK_MANAGER',
    email: 'bloodbank.manager@redcross.org',
    pass: 'BloodBank@12345',
    targetDashboard: '/blood-bank',
    description: 'Central Red Cross Blood Center, real inventory & emergency demand commitments.',
  },
  {
    roleName: 'Demo Donor',
    badge: 'DONOR',
    email: 'donor.rahul@example.com',
    pass: 'Donor@12345',
    targetDashboard: '/donor',
    description: 'Rahul Sharma (O- Universal Donor), live opportunity responses & donor profile.',
  },
];

export default function AdminLoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const user = useAuthStore((state) => state.user);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // If already logged in as ADMIN/SUPER_ADMIN, redirect to /admin
  React.useEffect(() => {
    if (isAuthenticated && user) {
      const roles = user.roles || (user.role ? [user.role] : []);
      if (roles.includes('SUPER_ADMIN') || roles.includes('ADMIN')) {
        router.replace('/admin');
      }
    }
  }, [isAuthenticated, user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await authService.login({
        email: email.trim(),
        password,
      });

      if (response.success && response.data) {
        setAuth(response.data.user, response.data.access_token);
        const destination = getDefaultDashboardPath(response.data.user);
        router.replace(destination);
      } else {
        setError(response.message || 'Invalid administrator/demo credentials. Please try again.');
      }
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || err.message || 'Invalid credentials. Please verify against seeded demo data.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const fillPersona = (persona: DemoPersona) => {
    setEmail(persona.email);
    setPassword(persona.pass);
    setError(null);
  };

  return (
    <div className="container mx-auto flex min-h-[calc(100vh-14rem)] max-w-xl items-center justify-center px-4 py-12">
      <Card className="w-full border-border/80 bg-card shadow-lg">
        <CardHeader className="space-y-2 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="lucide lucide-shield-alert"
            >
              <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
              <path d="M12 8v4" />
              <path d="M12 16h.01" />
            </svg>
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight">Admin &amp; Demo Governance Portal</CardTitle>
          <CardDescription className="text-xs text-muted-foreground">
            Administrative oversight, institutional statutory review, and 1-click evaluation demonstration access.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-5 pt-2">
          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-600 dark:text-red-400 font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Account Email"
              type="email"
              required
              placeholder="admin@lifelink.ai"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <Input
              label="Password"
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <Button type="submit" className="w-full font-semibold" disabled={loading}>
              {loading ? 'Authenticating against PostgreSQL...' : 'Sign In'}
            </Button>
          </form>

          {/* Demo Personas Section */}
          <div className="space-y-3 pt-2">
            <div className="relative py-1">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-[10px] uppercase">
                <span className="bg-card px-2 text-muted-foreground font-bold tracking-wider">
                  Seeded Demo Personas (Real PostgreSQL Data)
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {DEMO_PERSONAS.map((p) => (
                <div
                  key={p.email}
                  className="rounded-lg border border-border/80 bg-muted/30 p-2.5 space-y-1.5 transition-all hover:border-primary/40 hover:bg-muted/50 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-xs font-bold text-foreground">{p.roleName}</span>
                      <span className="text-[9px] bg-primary/10 text-primary px-1.5 py-0.2 rounded font-mono font-semibold">
                        {p.badge}
                      </span>
                    </div>
                    <p className="text-[10px] text-muted-foreground line-clamp-2 mt-0.5">
                      {p.description}
                    </p>
                    <div className="text-[10px] text-muted-foreground font-mono mt-1 space-y-0.5 bg-card/60 p-1.5 rounded border border-border/40">
                      <div className="truncate">Email: <span className="text-foreground">{p.email}</span></div>
                      <div>Pass: <span className="text-foreground">{p.pass}</span></div>
                    </div>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="w-full text-[11px] h-7 mt-1 border-primary/30 hover:bg-primary/10 text-primary font-medium"
                    onClick={() => fillPersona(p)}
                  >
                    Select {p.roleName}
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </CardContent>

        <CardFooter className="flex flex-col items-center justify-center space-y-2 text-center text-xs text-muted-foreground border-t border-border/50 pt-4">
          <div>
            Need to sign in through standard credentials?{' '}
            <Link href="/login" className="font-semibold text-primary hover:underline">
              Standard Login
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
