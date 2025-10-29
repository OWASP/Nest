import { ProgramStatusEnum } from 'types/__generated__/graphql'

export const mockPrograms = [
  {
    key: 'program_1',
    name: 'Program 1',
    description: 'This is a summary of Program 1.',
    startedAt: '2025-01-01',
    endedAt: '2025-12-31',
    status: ProgramStatusEnum.Published,
    modules: ['Module A', 'Module B'],
  },
]

export const mockProgramDetailsData = {
  getProgram: {
    key: 'test-program',
    name: 'Test Program',
    description: 'Sample summary',
    status: ProgramStatusEnum.Draft,
    startedAt: '2025-01-01',
    endedAt: '2025-12-31',
    menteesLimit: 20,
    experienceLevels: ['beginner', 'intermediate'],
    admins: [{ login: 'admin-user', avatarUrl: 'https://example.com/avatar.png' }],
    tags: ['web', 'security'],
    domains: ['OWASP'],
  },
  getProgramModules: [],
}

export default mockProgramDetailsData
