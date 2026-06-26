export const mockEvidence = {
  __typename: 'BoardCandidateClaimEvidenceNode' as const,
  id: 'evidence-1',
  key: 'certificate',
  name: 'Certificate',
  description: 'Certificate of completion.',
  sourceUrl: 'https://example.com/cert',
  hasFile: true,
  createdAt: '2025-01-16T10:00:00Z',
  updatedAt: '2025-01-16T10:00:00Z',
}

export const mockEvidences = [
  mockEvidence,
  {
    __typename: 'BoardCandidateClaimEvidenceNode' as const,
    id: 'evidence-2',
    key: 'reference-letter',
    name: 'Reference Letter',
    description: 'Reference letter.',
    sourceUrl: 'https://example.com/ref',
    hasFile: false,
    createdAt: '2025-01-17T10:00:00Z',
    updatedAt: '2025-01-17T10:00:00Z',
  },
]

export const mockClaimForEvidence = {
  __typename: 'BoardCandidateClaimNode' as const,
  id: 'claim-1',
  key: 'experience-leadership',
  name: 'Leadership Experience',
  description: 'Experience in leadership.',
  status: 'DRAFT',
  createdAt: '2025-01-15T10:00:00Z',
  updatedAt: '2025-01-15T10:00:00Z',
}

export const mockEvidenceFormData = {
  name: 'Certificate',
  description: 'Certificate of completion.',
  sourceUrl: 'https://example.com/cert',
  file: null,
}

export const mockGetClaimAndEvidencesData = {
  boardCandidateClaim: mockClaimForEvidence,
  boardCandidateClaimEvidences: mockEvidences,
}

export const mockGetClaimEvidenceData = {
  boardCandidateClaimEvidence: mockEvidence,
}

export const mockGetClaimEvidencesData = {
  boardCandidateClaimEvidences: mockEvidences,
}
