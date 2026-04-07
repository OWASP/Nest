export type SponsorTier = 'Diamond' | 'Platinum' | 'Gold' | 'Silver' | 'Supporter'

export type SponsorData = {
  id: string
  imageUrl: string
  name: string
  sponsorType: string
  url: string
  /** Shown on large-tier cards when API provides it (GraphQL may add later). */
  description?: string
  /** Diamond tier: short line shown in the editorial aside (GraphQL may add later). */
  motto?: string
}

export type SponsorsByTier = {
  tier: SponsorTier
  sponsors: SponsorData[]
}

export const TIER_ORDER: SponsorTier[] = ['Diamond', 'Platinum', 'Gold', 'Silver', 'Supporter']
