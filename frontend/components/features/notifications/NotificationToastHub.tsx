'use client';

// frontend/components/features/notifications/NotificationToastHub.tsx
// LifeLink AI — Real-Time WebSocket Toast & Audio Notification Hub
// Architecture Reference: ARCHITECTURE.md Section 15 & Section 22

import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

export interface LiveNotificationEvent {
  id: string;
  type: 'DONOR_ACCEPTED' | 'REQUEST_ESCALATED' | 'REQUEST_FULFILLED' | 'GENERAL';
  title: string;
  message: string;
  data?: {
    request_id?: string;
    request_number?: string;
    donor_name?: string;
    donor_blood_type?: string;
    hospital_name?: string;
    city?: string;
    timestamp?: string;
  };
  receivedAt: Date;
}

export function NotificationToastHub() {
  const router = useRouter();
  const [toasts, setToasts] = useState<LiveNotificationEvent[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Play synthesized medical chime using Web Audio API
  const playAlertChime = useCallback(() => {
    if (!soundEnabled) return;
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();

      // Double-beep emergency chime
      const now = ctx.currentTime;
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(880, now); // A5 note
      osc1.frequency.setValueAtTime(1174.66, now + 0.12); // D6 note
      gain1.gain.setValueAtTime(0.15, now);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.start(now);
      osc1.stop(now + 0.35);
    } catch {
      // AudioContext policy: browser might require user interaction first
    }
  }, [soundEnabled]);

  // Request browser Notification API permission
  useEffect(() => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      if (Notification.permission === 'default') {
        Notification.requestPermission().catch(() => {});
      }
    }
  }, []);

  const triggerDesktopNotification = useCallback((event: LiveNotificationEvent) => {
    if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
      try {
        new Notification(event.title, {
          body: event.message,
          icon: '/favicon.ico',
        });
      } catch {
        // Fallback for browsers that block notifications
      }
    }
  }, []);

  const connectWebSocket = useCallback(() => {
    if (typeof window === 'undefined') return;

    // Determine correct WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/v1/ws/hospital`;

    try {
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'CONNECTION_ESTABLISHED') return;

          const newToast: LiveNotificationEvent = {
            id: `${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
            type: payload.type || 'GENERAL',
            title: payload.title || 'LifeLink Alert',
            message: payload.message || 'New emergency coordination update received.',
            data: payload.data,
            receivedAt: new Date(),
          };

          playAlertChime();
          triggerDesktopNotification(newToast);

          setToasts((prev) => [newToast, ...prev.slice(0, 4)]);

          // Auto-dismiss after 10 seconds
          setTimeout(() => {
            setToasts((current) => current.filter((t) => t.id !== newToast.id));
          }, 10000);
        } catch {
          // Ignore unparseable frames
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Exponential/staggered reconnect attempt
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 5000);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket();
      }, 5000);
    }
  }, [playAlertChime, triggerDesktopNotification]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (socketRef.current) socketRef.current.close();
    };
  }, [connectWebSocket]);

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const handleNavigate = (toast: LiveNotificationEvent) => {
    dismissToast(toast.id);
    if (toast.data?.request_id) {
      router.push(`/hospital/requests/${toast.data.request_id}/matches`);
    } else if (toast.data?.request_number) {
      router.push(`/emergency/track/${toast.data.request_number}`);
    }
  };

  return (
    <>
      {/* Real-time connection badge on corner of dashboard */}
      <div className="fixed bottom-3 right-3 z-40 hidden sm:flex items-center gap-2 bg-card/90 backdrop-blur-md border border-border px-2.5 py-1 rounded-full text-[11px] shadow-sm text-text-muted">
        <span className="relative flex h-2 w-2">
          {isConnected ? (
            <>
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-success" />
            </>
          ) : (
            <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500" />
          )}
        </span>
        <span>{isConnected ? 'Real-Time Sync Active' : 'Connecting to Live Feed...'}</span>
        <button
          onClick={() => setSoundEnabled((v) => !v)}
          className="ml-1 text-xs hover:text-foreground transition-colors"
          title={soundEnabled ? 'Mute Alert Sound' : 'Enable Alert Sound'}
        >
          {soundEnabled ? '🔔' : '🔕'}
        </button>
      </div>

      {/* Floating Toast Notification Stack */}
      <aside aria-label="Real-time notifications" className="fixed top-16 sm:top-20 right-4 z-50 flex flex-col gap-3 max-w-sm sm:max-w-md w-full pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role="status"
            className="pointer-events-auto p-4 rounded-xl border-2 bg-card text-foreground shadow-2xl transition-all animate-in slide-in-from-top-4 duration-300 backdrop-blur-md flex flex-col gap-2.5 border-primary/40"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="text-xl">
                  {toast.type === 'DONOR_ACCEPTED'
                    ? '🩸'
                    : toast.type === 'REQUEST_FULFILLED'
                    ? '✅'
                    : '⚠️'}
                </span>
                <p className="font-bold text-sm text-foreground">{toast.title}</p>
              </div>
              <button
                onClick={() => dismissToast(toast.id)}
                className="text-text-muted hover:text-foreground text-sm font-bold leading-none p-1 rounded hover:bg-muted"
                aria-label="Close notification"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-muted-foreground leading-relaxed">{toast.message}</p>

            <div className="flex items-center justify-between pt-1 border-t border-border/60">
              <span className="text-[10px] text-text-muted">
                {toast.receivedAt.toLocaleTimeString()}
              </span>
              {(toast.data?.request_id || toast.data?.request_number) && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleNavigate(toast)}
                  className="text-xs h-7 px-3 font-semibold shadow-sm"
                >
                  View Details &rarr;
                </Button>
              )}
            </div>
          </div>
        ))}
      </aside>
    </>
  );
}
