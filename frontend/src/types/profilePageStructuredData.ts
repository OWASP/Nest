export interface ProfilePageStructuredData {
  '@context': string
  '@type': string
  mainEntity: {
    '@type': string
    name: string
    description?: string
    image?: string
    url?: string
    sameAs?: string[]
    worksFor?: {
      '@type': string
      name: string
    }
    address?: {
      '@type': string
      addressLocality: string
    }
    knowsAbout?: string[]
    hasOccupation?: {
      '@type': string
      name: string
    }
    memberOf?: {
      '@type': string
      name: string
      url: string
    }
  }
  interactionStatistic?: Array<{
    '@type': string
    interactionType: string
    userInteractionCount: number
  }>
}
