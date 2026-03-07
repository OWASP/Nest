import { apolloClient } from 'server/apolloClient'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import { GetMainPageDataDocument } from 'types/__generated__/homeQueries.generated'
import type { Chapter } from 'types/chapter'
import HomePageClient from './HomePageClient'

export default async function Home() {
  // Run both data fetches in parallel on the server.
  // The browser receives fully-rendered HTML — no client-side waterfall.
  const [graphQLResult, geoLocResult] = await Promise.allSettled([
    apolloClient.query({
      query: GetMainPageDataDocument,
      variables: { distinct: true },
    }),
    fetchAlgoliaData<Chapter>('chapters', '', 1, 1000),
  ])

  // Extract data, gracefully handling partial failures
  const graphQLData =
    graphQLResult.status === 'fulfilled' ? graphQLResult.value.data : null
  const geoLocData: Chapter[] =
    geoLocResult.status === 'fulfilled' ? geoLocResult.value.hits : []

  if (!graphQLData) {
    throw new Error('Failed to load home page data')
  }

  return (
    <HomePageClient
      graphQLData={graphQLData}
      geoLocData={geoLocData}
    />
  )
}
