import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
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
  startedAt: 1704067200,
  endedAt: 1735646400,
  userRole: 'admin',
}

describe('ProgramCard Accessibility', () => {
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
