import type { Certificate } from 'types/certificate'

export const mockCertificate: Certificate = {
  id: 'F9DD2BJ9ZYXW',
  issuedAt: '2024-08-07T03:47:53.000Z',
  isVerified: true,
  score: 350,
  tier: 'level 1',
  githubUser: {
    login: 'testuser',
    name: 'Test User',
    avatarUrl: 'https://avatars.githubusercontent.com/u/1234567?v=4',
  },
}

export const mockRevokedCertificate: Certificate = {
  ...mockCertificate,
  id: 'X7KP3MN2FOSS',
  isVerified: false,
  tier: 'level 2',
  score: 150,
}

export const mockCertificateNoName: Certificate = {
  ...mockCertificate,
  id: 'H4LQ8VW5OWHF',
  githubUser: {
    login: 'noname-user',
    name: undefined,
    avatarUrl: 'https://avatars.githubusercontent.com/u/9999999?v=4',
  },
}

export const mockMyCertificatesData = {
  myCertificates: [mockCertificate],
}

export const mockMyCertificatesMultipleData = {
  myCertificates: [
    mockCertificate,
    {
      ...mockRevokedCertificate,
      id: 'R2ST6YC1ZYXW',
      tier: 'level 3',
      issuedAt: '2023-05-15T10:00:00.000Z',
      score: 80,
    },
  ],
}

export const mockGetCertificateData = {
  certificate: mockCertificate,
}

export const mockGetRevokedCertificateData = {
  certificate: mockRevokedCertificate,
}
