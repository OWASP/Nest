import { ProfilePageStructuredData } from 'types/profilePageStructuredData'
import type { User } from 'types/user'

export const formatISODate = (input?: number | string | null): string => {
  if (input == null) {
    return '' // Fixed: Return empty string instead of undefined to satisfy 'string' return type
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
  const dateCreated = formatISODate(user.createdAt)
  const dateModified = formatISODate(user.updatedAt)
  const followersCount = user.followersCount ?? 0 // Fixed: Ensure it's a number

  return {
    '@context': 'https://schema.org',
    '@type': 'ProfilePage',
    ...(dateCreated && {
      dateCreated,
    }),
    ...(dateModified && {
      dateModified,
    }),
    mainEntity: {
      '@type': 'Person',
      ...(user.location && {
        address: user.location,
      }),
      description: user.bio || '',
      identifier: user.login || 'unknown',
      image: user.avatarUrl || '',
      ...(followersCount > 0 && {
        interactionStatistic: [
          {
            '@type': 'InteractionCounter',
            interactionType: 'https://schema.org/FollowAction',
            userInteractionCount: followersCount,
          },
        ],
      }),
      memberOf: {
        '@type': 'Organization',
        name: 'OWASP Community',
        url: 'https://nest.owasp.org/members',
      },
      name: user.name || user.login || 'OWASP Member',
      sameAs: user.url ? [user.url] : [], // Fixed: Handle possibly undefined url
      url: `${baseUrl}/members/${user.login || ''}`,
      ...(user.company && {
        worksFor: {
          '@type': 'Organization',
          name: user.company,
        },
      }),
    },
  }
}