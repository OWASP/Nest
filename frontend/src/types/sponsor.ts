export type SponsorTier = 'diamond' | 'platinum' | 'gold' | 'silver' | 'supporter'

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

export const TIER_ORDER: SponsorTier[] = ['diamond', 'platinum', 'gold', 'silver', 'supporter']

export const TIER_LABEL: Record<SponsorTier, string> = {
  diamond: 'Diamond',
  platinum: 'Platinum',
  gold: 'Gold',
  silver: 'Silver',
  supporter: 'Supporter',
}
