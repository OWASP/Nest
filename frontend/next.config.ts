
import { withSentryConfig } from '@sentry/nextjs'
import type { NextConfig } from 'next'

const forceStandalone = process.env.FORCE_STANDALONE === 'yes'
const isLocal = process.env.NEXT_PUBLIC_ENVIRONMENT === 'local'

const nextConfig: NextConfig = {
  devIndicators: false,
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          ...(isLocal ? [] : [
            {
              key: 'Strict-Transport-Security',
              value: 'max-age=31536000; includeSubDomains; preload'
            },
            {
              key: 'Content-Security-Policy',
              value: [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline'", 
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https:",
                // Removed the jogruber.de API host below
                "connect-src 'self' https://*.ingest.sentry.io https://us.i.posthog.com"
              ].join('; '),
            }
          ]),
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
        ],
      },
    ]
  },
  images: {
    // This is a list of remote patterns that Next.js will use to determine
    // if an image is allowed to be loaded from a remote source.
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'avatars.githubusercontent.com',
      },
      {
        protocol: 'https',
        hostname: 'owasp.org',
      },
      {
        protocol: 'https',
        hostname: 'raw.githubusercontent.com',
      },
      {
        protocol: 'https',
        hostname: '**.tile.openstreetmap.org',
      },
    ],
  },
  // https://nextjs.org/docs/app/api-reference/config/next-config-js/poweredByHeader
  poweredByHeader: false,
  // https://nextjs.org/docs/app/api-reference/config/next-config-js/productionBrowserSourceMaps
  productionBrowserSourceMaps: true,
  serverExternalPackages: ['import-in-the-middle', 'require-in-the-middle'],
  transpilePackages: ['@react-leaflet/core', 'leaflet', 'react-leaflet', 'react-leaflet-cluster'],
  ...(isLocal && !forceStandalone ? {} : { output: 'standalone' }),
}

export default withSentryConfig(nextConfig, {
  // https://www.npmjs.com/package/@sentry/webpack-plugin#options
  disableLogger: false,
  org: 'owasp-org',
  project: 'nest-frontend',
  release: {
    name: process.env.RELEASE_VERSION,
  },
  silent: isLocal,
  telemetry: false,
  widenClientFileUpload: true,
  ...(process.env.NEXT_SENTRY_AUTH_TOKEN
    ? {
        authToken: process.env.NEXT_SENTRY_AUTH_TOKEN,
        // https://docs.sentry.io/platforms/javascript/guides/nextjs/sourcemaps/
        sourcemaps: {
          deleteSourcemapsAfterUpload: true,
          disable: false,
          ignore: ['**/node_modules/**'],
        },
      }
    : {}),
})
