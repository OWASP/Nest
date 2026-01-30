import { ProfilePageStructuredData } from 'types/profilePageStructuredData'
import type { User } from 'types/user'

export const formatISODate = (input?: number | string): string | undefined => {
  if (input == null) {
    return undefined
  }

  const date =
    typeof input === 'number'
      ? new Date(input * 1000) // Unix timestamp in seconds
      : new Date(input) // ISO date string

  if (Number.isNaN(date.getTime())) {
    throw new TypeError('Invalid date')
  }

  return date.toISOString()
}

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
  user: User,
  baseUrl = 'https://nest.owasp.org'
): ProfilePageStructuredData {
  return {
    '@context': 'https://schema.org',
    '@type': 'ProfilePage',
    ...(formatISODate(user.createdAt) && {
      dateCreated: formatISODate(user.createdAt),
    }),
    ...(formatISODate(user.updatedAt) && {
      dateModified: formatISODate(user.updatedAt),
    }),
    mainEntity: {
      '@type': 'Person',
      ...(user.location && {
        address: user.location,
      }),
      description: user.bio || '',
      identifier: user.login,
      image: user.avatarUrl,
      ...((user.followersCount || 0) > 0 && {
        interactionStatistic: [
          {
            '@type': 'InteractionCounter',
            interactionType: 'https://schema.org/FollowAction',
            userInteractionCount: user.followersCount || 0,
          },
        ],
      }),
      memberOf: {
        '@type': 'Organization',
        name: 'OWASP Community',
        url: 'https://nest.owasp.org/members',
      },
      name: user.name || user.login,
      sameAs: user.url ? [user.url] : [],
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
