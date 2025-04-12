import type { NextConfig } from 'next'

const isLocal = process.env.NEXT_PUBLIC_ENVIRONMENT === 'local'

const nextConfig: NextConfig = {
  images: {
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

export default nextConfig
