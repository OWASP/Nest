
export const mockUserDetailsData = {
  user: {
    login: 'testuser',
    name: 'Test User',
    avatarUrl: 'https://example.com/avatar.jpg',
    url: 'https://github.com/testuser',
    bio: 'This is a test user',
    company: 'Test Company',
    location: 'Test Location',
    email: 'testuser@example.com',
    followersCount: 10,
    followingCount: 5,
    publicRepositoriesCount: 3,
    createdAt: 1723002473,
    issues: [
      {
        number: 1,
        title: 'Test Issue',
        createdAt: 1723002473,
        commentsCount: 5,
        repository: {
          key: 'test-repo',
          ownerKey: 'testuser'
        }
      }
    ],
    releases: [
      {
        name: 'v1.0.0',
        tagName: '1.0.0',
        isPreRelease: false,
        publishedAt: 1723002473,
        repository: {
          key: 'test-repo',
          ownerKey: 'testuser'
        }
      }
    ]
  }
}

