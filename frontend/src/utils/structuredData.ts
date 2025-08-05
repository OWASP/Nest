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
      hasOccupation: {
        '@type': 'Occupation',
        name: 'OWASP Community Member',
      },
      ...(user.company && {
        worksFor: {
          '@type': 'Organization',
          name: user.company,
        },
      }),
      ...(user.location && {
        address: {
          '@type': 'PostalAddress',
          addressLocality: user.location,
        },
      }),
    },
    ...(user.followersCount > 0 && {
      interactionStatistic: [
        {
          '@type': 'InteractionCounter',
          interactionType: 'https://schema.org/FollowAction',
          userInteractionCount: user.followersCount,
        },
      ],
    }),
  }

  return structuredData
}
