import { AlgoliaResponseType } from 'types/algolia'
import { ENVIRONMENT } from 'utils/credentials'
import { client } from 'utils/helpers/algoliaClient'
import { AppError } from 'wrappers/ErrorWrapper'

export const fetchAlgoliaGeoLoc = async <T>(): Promise<AlgoliaResponseType<T>> => {
  const indexName = 'chapters'
  try {
    const request = {
      attributesToHighlight: [],
      indexName: `${ENVIRONMENT}_${indexName}`,
      hitsPerPage: 1000,
      attributesToRetrieve: ['_geoloc'],
    }

    const { results } = await client.search({
      requests: [request],
    })
    if (results && results.length > 0) {
      const { hits } = results[0] as unknown as AlgoliaResponseType<T>
      return {
        hits: hits as T[],
      }
    } else {
      return { hits: [] }
    }
  } catch (error) {
    if (error instanceof AppError) {
      throw error
    }
    throw new AppError(500, 'Search service error')
  }
}
