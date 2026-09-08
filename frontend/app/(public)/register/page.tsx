'use client';

// frontend/app/(public)/register/page.tsx
// LifeLink AI — Voluntary Donor & Healthcare Registration
// Architecture Reference: ARCHITECTURE.md Section 18

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authService } from '@/services/authService';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

export default function RegisterPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);

  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('DONOR');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);

    // Client-side strict validation
    if (!firstName.trim() || /\d/.test(firstName)) {
      setErrorMessage('First name cannot contain numbers.');
      setIsLoading(false);
      return;
    }
    if (!lastName.trim() || /\d/.test(lastName)) {
      setErrorMessage('Last name cannot contain numbers.');
      setIsLoading(false);
      return;
    }

    try {
      const regResp = await authService.register({
        email: email.trim(),
        password,
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        phone: phone.trim() || undefined,
        role,
      });

      if (!regResp.success) {
        setErrorMessage(regResp.message || 'Registration failed.');
        setIsLoading(false);
        return;
      }

      const loginResp = await authService.login({
        email: email.trim(),
        password,
      });

      if (loginResp.success && loginResp.data) {
        setAuth(loginResp.data.user, loginResp.data.access_token);
        const { getDefaultDashboardPath } = await import('@/lib/auth');
        router.push(getDefaultDashboardPath(loginResp.data.user));
      } else {
        router.push('/login');
      }

    } catch (err: any) {
      const msg =
        err.response?.data?.error?.message ||
        err.message ||
        'Registration failed. Password must be 8+ chars with uppercase, number, and symbol.';
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="py-12 sm:py-20 flex items-center justify-center px-4">
      <div className="w-full max-w-lg">
        <Card className="border-border shadow-xl bg-card">
          <CardHeader className="text-center space-y-2 pb-4">
            <div className="mx-auto h-12 w-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center text-2xl mb-1">
              🩸
            </div>
            <CardTitle className="text-2xl font-bold">Create Your LifeLink Account</CardTitle>
            <CardDescription>
              Join the emergency blood &amp; healthcare coordination network
            </CardDescription>
          </CardHeader>

          <CardContent className="pt-2">
            <div className="flex justify-end text-[11px] text-muted-foreground mb-2">
              <span><span className="text-destructive font-bold">*</span> Required field</span>
            </div>

            {errorMessage && (
              <div className="mb-4 rounded-lg border border-critical/40 bg-critical/10 p-3 text-xs font-semibold text-critical" role="alert">
                {errorMessage}
              </div>
            )}

            <form onSubmit={handleRegister} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                    First Name <span className="text-destructive">*</span>
                  </label>
                  <Input
                    placeholder="Arjun"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                    Last Name <span className="text-destructive">*</span>
                  </label>
                  <Input
                    placeholder="Mehta"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                  Email Address <span className="text-destructive">*</span>
                </label>
                <Input
                  type="email"
                  placeholder="arjun.mehta@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Input
                  label="Phone Number (Optional)"
                  placeholder="+91 98765 43210"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
                <div>
                  <label htmlFor="role-select" className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                    Account Role <span className="text-destructive">*</span>
                  </label>
                  <select
                    id="role-select"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full h-10 rounded-lg border border-border bg-card px-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring font-medium"
                  >
                    <option value="DONOR">Voluntary Blood Donor</option>
                    <option value="PATIENT">Patient Attendant</option>
                    <option value="HOSPITAL_STAFF">Hospital Medical Staff</option>
                    <option value="BLOOD_BANK_STAFF">Blood Bank Coordinator</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                  Password <span className="text-destructive">*</span>
                </label>
                <Input
                  type="password"
                  placeholder="Min. 8 chars, 1 uppercase, 1 digit, 1 symbol"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              <div className="pt-2">
                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  className="w-full font-bold shadow-sm"
                  isLoading={isLoading}
                >
                  Create Account
                </Button>
              </div>
            </form>
          </CardContent>

          <CardFooter className="flex items-center justify-center border-t border-border/60 pt-4 text-xs text-muted-foreground">
            <p>
              Already registered?{' '}
              <Link href="/login" className="text-primary font-bold hover:underline">
                Sign In
              </Link>
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
