'use client';

// frontend/components/ui/Button.tsx
// LifeLink AI — Standardized Button Component
// Architecture Reference: ARCHITECTURE.md Section 15

import React from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: React.ReactNode;
}

const variantClasses: Record<NonNullable<ButtonProps['variant']>, string> = {
  // Brand CTA (LifeLink Crimson)
  primary:
    'bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm shadow-primary/20 active:scale-[0.98]',
  // Neutral secondary action
  secondary:
    'bg-secondary text-secondary-foreground hover:bg-muted border border-border active:scale-[0.98]',
  // Emergency / Critical Action (Semantically red)
  danger:
    'bg-critical text-white hover:bg-red-700 shadow-sm shadow-critical/30 active:scale-[0.98]',
  // Low priority / icon action
  ghost:
    'text-muted-foreground hover:bg-muted hover:text-foreground active:scale-[0.98]',
  // Clean outline action
  outline:
    'border border-border bg-transparent hover:bg-muted text-foreground active:scale-[0.98]',
};

const sizeClasses: Record<NonNullable<ButtonProps['size']>, string> = {
  sm: 'h-9 px-3 text-xs gap-1.5 min-w-[36px]',
  md: 'h-10 px-4 text-sm font-medium gap-2',
  lg: 'h-12 px-6 text-base font-semibold gap-2.5',
};

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  className,
  disabled,
  type = 'button',
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      aria-busy={isLoading}
      className={cn(
        'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-150 select-none',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background',
        variantClasses[variant],
        sizeClasses[size],
        disabled || isLoading ? 'opacity-50 cursor-not-allowed pointer-events-none' : 'cursor-pointer',
        className,
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      ) : null}
      {children}
    </button>
  );
}
