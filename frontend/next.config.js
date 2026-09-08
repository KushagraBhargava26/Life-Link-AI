/** @type {import('next').NextConfig} */

// frontend/next.config.js
// LifeLink AI — Next.js Configuration
// Architecture Reference: ARCHITECTURE.md Section 15 (Frontend Architecture)

const nextConfig = {
  // Use standalone output for Docker deployment
  output: 'standalone',

  // Strict mode for development — catches potential issues early
  reactStrictMode: true,

  // Disable x-powered-by header for security
  poweredByHeader: false,

  // Image optimization configuration
  images: {
    // Add allowed external image domains here as they are introduced
    remotePatterns: [],
    // Formats for optimization
    formats: ['image/avif', 'image/webp'],
  },

  // Environment variable exposure to the client
  // Only variables prefixed with NEXT_PUBLIC_ are exposed
  env: {
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'LifeLink AI',
    NEXT_PUBLIC_APP_VERSION: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
  },

  // Redirect root to app for cleaner URLs
  async redirects() {
    return [];
  },

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          // Prevent clickjacking
          { key: 'X-Frame-Options', value: 'DENY' },
          // Prevent MIME type sniffing
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          // Enable XSS protection in older browsers
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          // Referrer policy
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          // Permissions policy
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(self)',
          },
        ],
      },
    ];
  },

  // Webpack configuration (minimal overrides)
  webpack: (config) => {
    // Required for Leaflet.js server-side compatibility
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };
    return config;
  },
};

module.exports = nextConfig;
