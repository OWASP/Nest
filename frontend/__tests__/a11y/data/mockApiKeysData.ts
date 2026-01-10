export const mockApiKeys = {
  apiKeys: [
    {
      uuid: '1',
      name: 'mock key 1',
      isRevoked: false,
      createdAt: '2025-07-11T08:17:45.406011+00:00',
      expiresAt: null,
    },
    {
      uuid: '2',
      name: 'mock key 2',
      isRevoked: false,
      createdAt: '2025-07-11T07:36:44.115179+00:00',
      expiresAt: '2025-07-12T00:00:00+00:00',
    },
  ],
  activeApiKeyCount: 2,
}

export const mockCreateApiKeyResult = {
  data: {
    createApiKey: {
      rawKey: 'new-secret-api-key-12345',
      apiKey: {
        uuid: '4',
        name: 'Test Key',
        isRevoked: false,
        createdAt: '2025-07-11T10:00:00.000Z',
        expiresAt: null,
      },
    },
  },
}
