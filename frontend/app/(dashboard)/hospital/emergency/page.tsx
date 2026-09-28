'use client';

// frontend/app/(dashboard)/hospital/emergency/page.tsx
// Keep the legacy emergency-desk URL routed to the authenticated requisition workspace.

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HospitalEmergencyPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/hospital/requests');
  }, [router]);

  return (
    <div className="py-20 flex flex-col items-center justify-center space-y-3">
      <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
      <span className="text-sm text-muted-foreground">Opening hospital requisitions...</span>
    </div>
  );
}
