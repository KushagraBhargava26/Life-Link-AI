// frontend/app/layout.tsx
// LifeLink AI — Root Layout
// Architecture Reference: ARCHITECTURE.md Section 15 (Frontend Architecture)
//
// The root layout wraps every page in the application.
// Provides: font loading, global metadata, theme provider placeholder.
//
// Phase 1.1: Minimal layout — only structure, no business logic.

import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';

// ---------------------------------------------------------------------------
// Google Fonts — Inter (Architecture.md Section 15)
// ---------------------------------------------------------------------------
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

// ---------------------------------------------------------------------------
// SEO Metadata
// ---------------------------------------------------------------------------
export const metadata: Metadata = {
  title: {
    default: 'LifeLink AI — Emergency Blood & Organ Intelligence Platform',
    template: '%s | LifeLink AI',
  },
  description:
    'AI-powered platform connecting patients, blood donors, hospitals, and blood banks for emergency blood coordination. Find compatible donors in minutes.',
  keywords: [
    'blood donation',
    'emergency blood',
    'blood bank',
    'organ donation',
    'AI matching',
    'India',
  ],
  authors: [{ name: 'LifeLink AI Team' }],
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_IN',
    siteName: 'LifeLink AI',
    title: 'LifeLink AI — Emergency Blood & Organ Intelligence Platform',
    description:
      'AI-powered emergency blood and organ coordination platform for India.',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#dc2626',
};

// ---------------------------------------------------------------------------
// Root Layout Component
// ---------------------------------------------------------------------------
import { ThemeProvider } from '@/components/ui/ThemeProvider';

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                const saved = localStorage.getItem('lifelink-theme');
                if (saved === 'light') {
                  document.documentElement.classList.remove('dark');
                  document.documentElement.style.colorScheme = 'light';
                } else {
                  document.documentElement.classList.add('dark');
                  document.documentElement.style.colorScheme = 'dark';
                }
              } catch (e) {}
            `,
          }}
        />
      </head>
      <body className="min-h-screen bg-background text-foreground antialiased">
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
