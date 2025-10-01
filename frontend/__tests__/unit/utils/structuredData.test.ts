import type { User } from 'types/user'
import { generateProfilePageStructuredData } from 'utils/structuredData'

describe('generateProfilePageStructuredData', () => {
  const mockUser: User = {
    avatarUrl: 'https://example.com/avatar.jpg',
    bio: 'Security researcher and OWASP contributor',
    company: 'Security Corp',
    contributionsCount: 150,
    createdAt: '2020-01-01T00:00:00Z',
    email: 'user@example.com',
    followersCount: 500,
    followingCount: 200,
    key: 'testuser',
    location: 'San Francisco, CA, USA',
    login: 'testuser',
    name: 'Test User',
    publicRepositoriesCount: 25,
    updatedAt: '2021-02-03T00:00:00Z',
    url: 'https://github.com/testuser',
  }

  it('should generate valid ProfilePage structured data', () => {
    const result = generateProfilePageStructuredData(mockUser)

    expect(result).toEqual({
      '@context': 'https://schema.org',
      '@type': 'ProfilePage',
      dateCreated: '2020-01-01T00:00:00.000Z',
      dateModified: '2021-02-03T00:00:00.000Z',
      mainEntity: {
        '@type': 'Person',
        address: 'San Francisco, CA, USA',
        description: 'Security researcher and OWASP contributor',
        identifier: 'testuser',
        image: 'https://example.com/avatar.jpg',
        interactionStatistic: [
          {
            '@type': 'InteractionCounter',
            interactionType: 'https://schema.org/FollowAction',
            userInteractionCount: 500,
          },
        ],
        memberOf: {
          '@type': 'Organization',
          name: 'OWASP Community',
          url: 'https://nest.owasp.org/members',
        },
        name: 'Test User',
        sameAs: ['https://github.com/testuser'],
        url: 'https://nest.owasp.org/members/testuser',
        worksFor: {
          '@type': 'Organization',
          name: 'Security Corp',
        },
      },
    })
  })

  it('should handle user without optional fields', () => {
    const minimalUser: User = {
      avatarUrl: 'https://example.com/avatar.jpg',
      contributionsCount: 0,
      createdAt: '2020-01-01T00:00:00Z',
      followersCount: 0,
      followingCount: 0,
      key: 'basicuser',
      login: 'basicuser',
      publicRepositoriesCount: 0,
      updatedAt: '2021-02-03T00:00:00Z',
      url: 'https://github.com/basicuser',
    }

    const result = generateProfilePageStructuredData(minimalUser)

    expect(result.mainEntity.name).toBe('basicuser')
    expect(result.mainEntity.description).toBeUndefined()
    expect(result.mainEntity.worksFor).toBeUndefined()
    expect(result.mainEntity.address).toBeUndefined()
    expect(result.mainEntity.interactionStatistic).toBeUndefined()

    // These should always be present
    expect(result.mainEntity.memberOf).toBeDefined()
  })

  it('should include interaction statistics only when followers count > 0', () => {
    const userWithFollowers = { ...mockUser, followersCount: 100 }
    const userWithoutFollowers = { ...mockUser, followersCount: 0 }

    const resultWithFollowers = generateProfilePageStructuredData(userWithFollowers)
    const resultWithoutFollowers = generateProfilePageStructuredData(userWithoutFollowers)

    expect(resultWithFollowers.mainEntity.interactionStatistic).toBeDefined()
    expect(resultWithFollowers.mainEntity.interactionStatistic?.[0].userInteractionCount).toBe(100)

    expect(resultWithoutFollowers.mainEntity.interactionStatistic).toBeUndefined()
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

    expect(result.mainEntity.address).toEqual('New York, NY')
    expect(result.mainEntity.worksFor).toBeUndefined()
  })

  it('should fallback to login when name is not provided', () => {
    const userWithoutName = { ...mockUser, name: undefined }

    const result = generateProfilePageStructuredData(userWithoutName)

    expect(result.mainEntity.name).toBe('testuser')
  })
})
