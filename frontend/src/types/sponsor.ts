export type SponsorTier = 'Diamond' | 'Platinum' | 'Gold' | 'Silver' | 'Supporter'

export type SponsorData = {
  id: string
  imageUrl: string
  name: string
  sponsorType: string
  url: string
  /** Diamond tier: short line when API provides it (GraphQL may add later). */
  motto?: string
}

export type SponsorsByTier = {
  tier: SponsorTier
  sponsors: SponsorData[]
}

export const TIER_ORDER: SponsorTier[] = ['Diamond', 'Platinum', 'Gold', 'Silver', 'Supporter']
