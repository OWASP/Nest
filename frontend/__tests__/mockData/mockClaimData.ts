export const mockClaims = [
  {
    key: 'experience-web-security',
    name: 'Web Security Experience',
    description: 'Experience in web security.',
    status: 'DRAFT',
    hasEvidence: true,
    order: 1,
    createdAt: '2025-01-15T10:00:00Z',
    updatedAt: '2025-01-15T10:00:00Z',
  },
  {
    key: 'chapter-leadership',
    name: 'Chapter Leadership',
    description: 'Led OWASP chapter meetings.',
    status: 'SUBMITTED',
    hasEvidence: false,
    order: 2,
    createdAt: '2025-01-20T10:00:00Z',
    updatedAt: '2025-01-20T10:00:00Z',
  },
  {
    key: 'approved-claim',
    name: 'Approved Claim',
    description: 'Approved claim with evidence.',
    status: 'APPROVED',
    hasEvidence: true,
    order: 1,
    createdAt: '2025-02-01T10:00:00Z',
    updatedAt: '2025-02-01T10:00:00Z',
  },
  {
    key: 'rejected-claim',
    name: 'Rejected Claim',
    description: 'Rejected claim.',
    status: 'REJECTED',
    hasEvidence: false,
    order: 1,
    createdAt: '2025-02-10T10:00:00Z',
    updatedAt: '2025-02-10T10:00:00Z',
  },
  {
    key: 'withdrawn-claim',
    name: 'Withdrawn Claim',
    description: 'Withdrawn claim.',
    status: 'WITHDRAWN',
    hasEvidence: false,
    order: 1,
    createdAt: '2025-02-15T10:00:00Z',
    updatedAt: '2025-02-15T10:00:00Z',
  },
  {
    key: 'discarded-claim',
    name: 'Discarded Claim',
    description: 'Discarded claim.',
    status: 'DISCARDED',
    hasEvidence: false,
    order: 1,
    createdAt: '2025-02-20T10:00:00Z',
    updatedAt: '2025-02-20T10:00:00Z',
  },
]

export const mockCandidateData = {
  boardOfDirectors: {
    candidate: {
      id: 'candidate-1',
    },
  },
}

export const mockSingleClaim = {
  key: 'experience-web-security',
  name: 'Web Security Experience',
  description: 'Experience in web security.',
  status: 'DRAFT',
  createdAt: '2025-01-15T10:00:00Z',
  updatedAt: '2025-01-15T10:00:00Z',
}

export const mockEvidences = [
  {
    key: 'certificate',
    name: 'Certificate',
    description: 'Certificate of completion.',
    sourceUrl: 'https://example.com/cert',
    hasFile: true,
    createdAt: '2025-01-16T10:00:00Z',
    updatedAt: '2025-01-16T10:00:00Z',
  },
  {
    key: 'reference-letter',
    name: 'Reference Letter',
    description: 'Reference letter.',
    sourceUrl: 'https://example.com/ref',
    hasFile: false,
    createdAt: '2025-01-17T10:00:00Z',
    updatedAt: '2025-01-17T10:00:00Z',
  },
]
