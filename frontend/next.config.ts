import { withSentryConfig } from '@sentry/nextjs'
import type { NextConfig } from 'next'

const isLocal = process.env.NEXT_PUBLIC_ENVIRONMENT === 'local'

const nextConfig: NextConfig = {
  images: {
    // This is a list of remote patterns that Next.js will use to determine if an image is allowed to be loaded from a remote source.
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
  devIndicators: false,
  ...(isLocal ? {} : { output: 'standalone' }),
}

export default withSentryConfig(nextConfig, {
  // For all available options, see:
  // https://www.npmjs.com/package/@sentry/webpack-plugin#options
  org: 'OWASP',
  project: 'Nest',
  // Upload a larger set of source maps for prettier stack traces (increases build time)
  widenClientFileUpload: true,
  //suppress errors
  disableLogger: false,
})
