import { ProfilePageStructuredData } from 'types/profilePageStructuredData'
import type { UserDetails } from 'types/user'

/**
 * JSON-LD structure data for ProfilePage
 * https://developers.google.com/search/docs/appearance/structured-data/profile-page
 *
 * - @context: "https://schema.org"
 * - @type: "ProfilePage"
 * - mainEntity: A Person or Organization (using type Person for OWASP community members)
 *
 */
export function generateProfilePageStructuredData(
  user: UserDetails,
  baseUrl = 'https://nest.owasp.org'
): ProfilePageStructuredData {
  const profileUrl = `${baseUrl}/members/${user.login}`

  const structuredData: ProfilePageStructuredData = {
    '@context': 'https://schema.org',
    '@type': 'ProfilePage',
    mainEntity: {
      '@type': 'Person',
      name: user.name || user.login,
      description: user.bio,
      image: user.avatarUrl,
      url: profileUrl,
      sameAs: [user.url], // GitHub profile URL
      memberOf: {
        '@type': 'Organization',
        name: 'OWASP',
        url: 'https://owasp.org',
      },
    },
  }

  if (user.company) {
    structuredData.mainEntity.worksFor = {
      '@type': 'Organization',
      name: user.company,
    }
  }

  if (user.avatarUrl) {
    structuredData.mainEntity.image = user.avatarUrl
  }

  if (user.location) {
    structuredData.mainEntity.address = {
      '@type': 'PostalAddress',
      addressLocality: user.location,
    }
  }

  structuredData.mainEntity.knowsAbout = [
    'Application Security',
    'OWASP',
    'Cybersecurity',
    'Software Security',
  ]

  structuredData.mainEntity.hasOccupation = {
    '@type': 'Occupation',
    name: 'OWASP Community Member',
  }

  if (user.followersCount > 0) {
    structuredData.interactionStatistic = [
      {
        '@type': 'InteractionCounter',
        interactionType: 'https://schema.org/FollowAction',
        userInteractionCount: user.followersCount,
      },
    ]
  }

  return structuredData
}
