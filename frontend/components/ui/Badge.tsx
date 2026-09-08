// frontend/components/ui/Badge.tsx
// LifeLink AI — Semantic Status Badge Component
// Architecture Reference: ARCHITECTURE.md Section 15

import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps {
  variant?: 'default' | 'critical' | 'high' | 'medium' | 'low' | 'success' | 'info' | 'warning' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  className?: string;
}

export function Badge({ variant = 'default', size = 'md', children, className }: BadgeProps) {
  const variantClasses = {
    default: 'bg-secondary text-secondary-foreground border border-border',
    critical: 'bg-critical/15 text-critical border border-critical/30 font-semibold',
    high: 'bg-warning/15 text-warning border border-warning/30 font-semibold',
    warning: 'bg-warning/15 text-warning border border-warning/30 font-semibold',
    medium: 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30',
    low: 'bg-success/15 text-success border border-success/30 font-medium',
    success: 'bg-success/15 text-success border border-success/30 font-medium',
    info: 'bg-info/15 text-info border border-info/30 font-medium',
    outline: 'border border-border text-foreground bg-transparent',
  };

  const sizeClasses = {
    sm: 'px-2 py-0.2 text-[10px]',
    md: 'px-2.5 py-0.5 text-xs',
    lg: 'px-3 py-1 text-sm',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-medium tracking-wide transition-colors',
        variantClasses[variant],
        sizeClasses[size],
        className,
      )}
    >
      {children}
    </span>
  );
}
