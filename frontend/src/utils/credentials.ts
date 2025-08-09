export const API_URL = process.env.NEXT_PUBLIC_API_URL
export const CSRF_URL = process.env.NEXT_PUBLIC_CSRF_URL
export const ENVIRONMENT = process.env.NEXT_PUBLIC_ENVIRONMENT
export const GITHUB_CLIENT_ID = process.env.NEXT_SERVER_GITHUB_CLIENT_ID
export const GITHUB_CLIENT_SECRET = process.env.NEXT_SERVER_GITHUB_CLIENT_SECRET
export const GRAPHQL_URL = process.env.NEXT_PUBLIC_GRAPHQL_URL
export const GTM_ID = process.env.NEXT_PUBLIC_GTM_ID
export const IDX_URL = process.env.NEXT_PUBLIC_IDX_URL
export const IS_GITHUB_AUTH_ENABLED = Boolean(
  process.env.NEXT_SERVER_GITHUB_CLIENT_ID && process.env.NEXT_SERVER_GITHUB_CLIENT_SECRET
)
export const IS_PROJECT_HEALTH_ENABLED =
  process.env.NEXT_PUBLIC_IS_PROJECT_HEALTH_ENABLED === 'true'
export const NEXTAUTH_SECRET = process.env.NEXTAUTH_SECRET
export const NEXTAUTH_URL = process.env.NEXTAUTH_URL
export const RELEASE_VERSION = process.env.NEXT_PUBLIC_RELEASE_VERSION
export const SENTRY_AUTH_TOKEN = process.env.NEXT_SENTRY_AUTH_TOKEN
export const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN
