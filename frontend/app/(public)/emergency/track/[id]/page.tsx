'use client';

import { useParams } from 'next/navigation';
import { RequestTrackingView } from '@/components/features/emergency/RequestTrackingView';

export default function PublicEmergencyTrackingPage() {
  const params = useParams();
  const requestId = typeof params?.id === 'string' ? params.id : '';
  return <RequestTrackingView requestId={requestId} isPublic />;
}
