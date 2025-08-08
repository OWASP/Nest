export interface ProfilePageStructuredData {
  '@context': string
  '@type': string
  dateCreated?: string
  dateModified?: string
  mainEntity: {
    '@type': string
    address?: string
    description?: string
    identifier?: string
    image?: string
    interactionStatistic?: Array<{
      '@type': string
      interactionType: string
      userInteractionCount: number
    }>
    knowsAbout?: string[]
    memberOf?: {
      '@type': string
      name: string
      url: string
    }
    name: string
    sameAs?: string[]
    url?: string
    worksFor?: {
      '@type': string
      name: string
    }
  }
}
