import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { ProgramStatusEnum } from 'types/__generated__/graphql'
import { Program } from 'types/mentorship'
import ProgramCard from 'components/ProgramCard'

jest.mock('hooks/useUpdateProgramStatus', () => ({
  useUpdateProgramStatus: () => ({ updateProgramStatus: jest.fn() }),
}))

const baseMockProgram: Program = {
  id: '1',
  key: 'test-program',
  name: 'Test Program',
  description: 'This is a test program description',
  status: ProgramStatusEnum.Published,
  startedAt: '2024-01-01T00:00:00Z',
  endedAt: '2024-12-31T12:00:00Z',
  userRole: 'admin',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ProgramCard Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(
      <main>
        <ProgramCard program={baseMockProgram} href="/test/path" isAdmin accessLevel="admin" />
      </main>
    )
    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
