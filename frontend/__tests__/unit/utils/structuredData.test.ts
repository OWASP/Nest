import type { UserDetails } from 'types/user'
import { generateProfilePageStructuredData } from 'utils/structuredData'

describe('generateProfilePageStructuredData', () => {
  const mockUser: UserDetails = {
    avatarUrl: 'https://example.com/avatar.jpg',
    bio: 'Security researcher and OWASP contributor',
    company: 'Security Corp',
    contributionsCount: 150,
    createdAt: '2020-01-01T00:00:00Z',
    email: 'user@example.com',
    followersCount: 500,
    followingCount: 200,
    key: 'testuser',
    location: 'San Francisco, CA',
    login: 'testuser',
    name: 'Test User',
    publicRepositoriesCount: 25,
    url: 'https://github.com/testuser',
  }

  it('should generate valid ProfilePage structured data', () => {
    const result = generateProfilePageStructuredData(mockUser)

    expect(result).toEqual({
      '@context': 'https://schema.org',
      '@type': 'ProfilePage',
      mainEntity: {
        '@type': 'Person',
        name: 'Test User',
        description: 'Security researcher and OWASP contributor',
        image: 'https://example.com/avatar.jpg',
        url: 'https://nest.owasp.org/members/testuser',
        sameAs: ['https://github.com/testuser'],
        memberOf: {
          '@type': 'Organization',
          name: 'OWASP',
          url: 'https://owasp.org',
        },
        hasOccupation: {
          '@type': 'Occupation',
          name: 'OWASP Community Member',
        },
        worksFor: {
          '@type': 'Organization',
          name: 'Security Corp',
        },
        address: {
          '@type': 'PostalAddress',
          addressLocality: 'San Francisco, CA',
        },
      },
      interactionStatistic: [
        {
          '@type': 'InteractionCounter',
          interactionType: 'https://schema.org/FollowAction',
          userInteractionCount: 500,
        },
      ],
    })
  })

  it('should handle user without optional fields', () => {
    const minimalUser: UserDetails = {
      avatarUrl: 'https://example.com/avatar.jpg',
      contributionsCount: 0,
      createdAt: '2020-01-01T00:00:00Z',
      followersCount: 0,
      followingCount: 0,
      key: 'basicuser',
      login: 'basicuser',
      publicRepositoriesCount: 0,
      url: 'https://github.com/basicuser',
    }

    const result = generateProfilePageStructuredData(minimalUser)

    expect(result.mainEntity.name).toBe('basicuser')
    expect(result.mainEntity.description).toBeUndefined()
    expect(result.mainEntity.worksFor).toBeUndefined()
    expect(result.mainEntity.address).toBeUndefined()
    expect(result.interactionStatistic).toBeUndefined()

    // These should always be present
    expect(result.mainEntity.memberOf).toBeDefined()
    expect(result.mainEntity.hasOccupation).toBeDefined()
  })

  it('should include interaction statistics only when followers count > 0', () => {
    const userWithFollowers = { ...mockUser, followersCount: 100 }
    const userWithoutFollowers = { ...mockUser, followersCount: 0 }

    const resultWithFollowers = generateProfilePageStructuredData(userWithFollowers)
    const resultWithoutFollowers = generateProfilePageStructuredData(userWithoutFollowers)

    expect(resultWithFollowers.interactionStatistic).toBeDefined()
    expect(resultWithFollowers.interactionStatistic?.[0].userInteractionCount).toBe(100)

    expect(resultWithoutFollowers.interactionStatistic).toBeUndefined()
  })

  it('should use custom base URL when provided', () => {
    const result = generateProfilePageStructuredData(mockUser, 'https://custom.example.com')

    expect(result.mainEntity.url).toBe('https://custom.example.com/members/testuser')
  })

  it('should handle user with company but no location', () => {
    const userWithCompanyOnly = {
      ...mockUser,
      company: 'Tech Corp',
      location: undefined,
    }

    const result = generateProfilePageStructuredData(userWithCompanyOnly)

    expect(result.mainEntity.worksFor).toEqual({
      '@type': 'Organization',
      name: 'Tech Corp',
    })
    expect(result.mainEntity.address).toBeUndefined()
  })

  it('should handle user with location but no company', () => {
    const userWithLocationOnly = {
      ...mockUser,
      company: undefined,
      location: 'New York, NY',
    }

    const result = generateProfilePageStructuredData(userWithLocationOnly)

    expect(result.mainEntity.address).toEqual({
      '@type': 'PostalAddress',
      addressLocality: 'New York, NY',
    })
    expect(result.mainEntity.worksFor).toBeUndefined()
  })

  it('should fallback to login when name is not provided', () => {
    const userWithoutName = { ...mockUser, name: undefined }

    const result = generateProfilePageStructuredData(userWithoutName)

    expect(result.mainEntity.name).toBe('testuser')
  })
})
