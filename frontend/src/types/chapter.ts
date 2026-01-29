import type { Contributor } from 'types/contributor'
import type { Leader } from 'types/leader'

export type Chapter = {
  _geoloc?: GeoLocation
  contributionData?: Record<string, number>
  contributionStats?: {
    commits: number
    issues: number
    pullRequests: number
    releases: number
    total: number
  }
  createdAt?: number
  entityLeaders?: Leader[]
  geoLocation?: GeoLocation | null
  isActive?: boolean
  key: string
  leaders?: string[]
  name: string
  objectID?: string
  region?: string
  relatedUrls?: string[]
  suggestedLocation?: string | null
  summary?: string
  topContributors?: Contributor[]
  updatedAt?: number
  url?: string
}

export type GeoLocation = {
  lat: number
  lng: number
}
