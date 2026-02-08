import { ProgramStatusEnum } from 'types/__generated__/graphql'

export const mockPrograms = [
  {
    key: 'program_1',
    name: 'Program 1',
    description: 'This is a summary of Program 1.',
    startedAt: 1735689600,
    endedAt: 1767139200,
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
    startedAt: 1735689600,
    endedAt: 1767139200,
    menteesLimit: 20,
    experienceLevels: ['beginner', 'intermediate'],
    admins: [{ login: 'admin-user', avatarUrl: 'https://example.com/avatar.png' }],
    tags: ['web', 'security'],
    domains: ['OWASP'],
  },
  getProgramModules: [],
}

export default mockProgramDetailsData
