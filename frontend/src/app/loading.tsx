import LoadingSpinner from 'components/LoadingSpinner'

/**
 * Next.js streaming loading UI for the home page.
 * Shown automatically while the async Server Component (page.tsx)
 * awaits the parallel GraphQL + Algolia fetches on the server.
 *
 * This replaces the previous manual `if (isLoading) return <LoadingSpinner />`
 * check that required a client component to render.
 */
export default function Loading() {
    return <LoadingSpinner />
}
