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
  return {
    '@context': 'https://schema.org',
    '@type': 'ProfilePage',
    dateCreated: new Date(parseInt(user.createdAt) * 1000).toISOString(),
    dateModified: new Date(parseInt(user.updatedAt) * 1000).toISOString(),
    mainEntity: {
      '@type': 'Person',
      ...(user.location && {
        address: user.location,
      }),
      description: user.bio,
      identifier: user.login,
      image: user.avatarUrl,
      ...(user.followersCount > 0 && {
        interactionStatistic: [
          {
            '@type': 'InteractionCounter',
            interactionType: 'https://schema.org/FollowAction',
            userInteractionCount: user.followersCount,
          },
        ],
      }),
      memberOf: {
        '@type': 'Organization',
        name: 'OWASP Community',
        url: 'https://nest.owasp.org/members',
      },
      name: user.name || user.login,
      sameAs: [user.url],
      url: `${baseUrl}/members/${user.login}`,
      ...(user.company && {
        worksFor: {
          '@type': 'Organization',
          name: user.company,
        },
      }),
    },
  }
}
