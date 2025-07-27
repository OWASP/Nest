import { withSentryConfig } from '@sentry/nextjs'
import type { NextConfig } from 'next'
import { SENTRY_AUTH_TOKEN } from 'utils/credentials'

const isLocal = process.env.NEXT_PUBLIC_ENVIRONMENT === 'local'

const nextConfig: NextConfig = {
  devIndicators: false,
  // https://nextjs.org/docs/app/api-reference/config/next-config-js/productionBrowserSourceMaps
  productionBrowserSourceMaps: true,
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
  authToken: SENTRY_AUTH_TOKEN,
  widenClientFileUpload: true,
  // https://docs.sentry.io/platforms/javascript/guides/nextjs/sourcemaps/
  sourcemaps: {
    disable: false, // Enable source maps
    assets: ['**/*.js', '**/*.js.map'], // Specify which files to upload
    ignore: ['**/node_modules/**'], // Files to exclude
    deleteSourcemapsAfterUpload: true, // Security: delete after upload
  },
  disableLogger: false,
})
