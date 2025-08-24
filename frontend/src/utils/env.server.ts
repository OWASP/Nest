import 'server-only'

export const GITHUB_CLIENT_ID = process.env.NEXT_SERVER_GITHUB_CLIENT_ID!;
export const GITHUB_CLIENT_SECRET = process.env.NEXT_SERVER_GITHUB_CLIENT_SECRET!;
export const NEXTAUTH_URL = process.env.NEXTAUTH_URL
export const SENTRY_AUTH_TOKEN = process.env.NEXT_SENTRY_AUTH_TOKEN

export function isGithubAuthEnabled() {
    return Boolean(GITHUB_CLIENT_ID && GITHUB_CLIENT_SECRET);
}