import { withSentryConfig } from '@sentry/nextjs'
import type { NextConfig } from 'next'

const isLocal = process.env.NEXT_PUBLIC_ENVIRONMENT === 'local'

const nextConfig: NextConfig = {
   productionBrowserSourceMaps: true, // Enable source maps for production
  // ...existing config...
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
  serverExternalPackages: ['import-in-the-middle', 'require-in-the-middle'],
  turbopack: {
    resolveExtensions: ['.ts', '.tsx', '.mjs', '.json', '.yaml', '.js', '.jsx'],
  },
  ...(isLocal ? {} : { output: 'standalone' }),
}

export default withSentryConfig(nextConfig, {
  // https://www.npmjs.com/package/@sentry/webpack-plugin#options
  org: 'OWASP',
  project: 'Nest',
  widenClientFileUpload: true,
  disableLogger: false,
})
