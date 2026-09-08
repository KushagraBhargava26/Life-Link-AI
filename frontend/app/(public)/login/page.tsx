'use client';

// frontend/app/(public)/login/page.tsx
// LifeLink AI — Sign In
// Architecture Reference: ARCHITECTURE.md Section 18

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authService } from '@/services/authService';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

import { getDefaultDashboardPath } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await authService.login({
        email: email.trim(),
        password,
      });

      if (response.success && response.data) {
        setAuth(response.data.user, response.data.access_token);
        router.push(getDefaultDashboardPath(response.data.user));
      } else {
        setErrorMessage(response.message || 'Authentication failed.');
      }

    } catch (err: any) {
      const msg = err.response?.data?.error?.message || err.message || 'Invalid email or password.';
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="py-12 sm:py-20 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <Card className="border-border shadow-xl bg-card">
          <CardHeader className="text-center space-y-2 pb-4">
            <div className="mx-auto h-12 w-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center text-2xl mb-1">
              🩸
            </div>
            <CardTitle className="text-2xl font-bold">Sign In to LifeLink</CardTitle>
            <CardDescription>
              Access your voluntary donor profile or healthcare dashboard
            </CardDescription>
          </CardHeader>

          <CardContent className="pt-2">
            {errorMessage && (
              <div className="mb-4 rounded-lg border border-critical/40 bg-critical/10 p-3 text-xs font-semibold text-critical" role="alert">
                {errorMessage}
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <Input
                label="Email Address"
                type="email"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              <div className="pt-2">
                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  className="w-full font-bold shadow-sm"
                  isLoading={isLoading}
                >
                  Sign In
                </Button>
              </div>
            </form>
          </CardContent>

          <CardFooter className="flex flex-col items-center justify-center gap-2 border-t border-border/60 pt-4 text-xs text-muted-foreground">
            <p>
              Don&apos;t have an account?{' '}
              <Link href="/register" className="text-primary font-bold hover:underline">
                Register as Voluntary Donor
              </Link>
            </p>
            <p>
              Immediate trauma emergency?{' '}
              <Link href="/emergency" className="text-critical font-semibold hover:underline">
                Public Emergency Intake
              </Link>
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
