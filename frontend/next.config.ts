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
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              isLocal
                ? "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://owasp-nest.s3.amazonaws.com https://owasp-nest-production.s3.amazonaws.com https://www.googletagmanager.com https://*.i.posthog.com https://*.tile.openstreetmap.org"
                : "script-src 'self' 'unsafe-inline' https://owasp-nest.s3.amazonaws.com https://owasp-nest-production.s3.amazonaws.com https://www.googletagmanager.com https://*.i.posthog.com https://*.tile.openstreetmap.org",
              "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://owasp-nest.s3.amazonaws.com https://owasp-nest-production.s3.amazonaws.com",
              "img-src 'self' data: https://authjs.dev https://avatars.githubusercontent.com https://*.tile.openstreetmap.org https://owasp.org https://owasp-nest.s3.amazonaws.com https://owasp-nest-production.s3.amazonaws.com https://raw.githubusercontent.com",
              "font-src 'self' https://cdn.jsdelivr.net",
              "connect-src 'self' https://github-contributions-api.jogruber.de https://*.google-analytics.com https://*.i.posthog.com https://*.sentry.io https://*.tile.openstreetmap.org",
              "object-src 'none'",
              "frame-src 'self'",
              "frame-ancestors 'none'",
              "base-uri 'self'",
              "form-action 'self'",
            ].join('; '),
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), fullscreen=(self), geolocation=(self), microphone=()',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
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
