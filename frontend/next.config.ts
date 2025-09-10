import { withSentryConfig } from '@sentry/nextjs'
import type { NextConfig } from 'next'

const isLocal = process.env.NEXT_PUBLIC_ENVIRONMENT === 'local'

const nextConfig: NextConfig = {
  devIndicators: false,
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
  // https://nextjs.org/docs/app/api-reference/config/next-config-js/productionBrowserSourceMaps
  productionBrowserSourceMaps: true,
  serverExternalPackages: ['import-in-the-middle', 'require-in-the-middle'],
  ...(isLocal ? {} : { output: 'standalone' }),
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
