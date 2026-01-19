import { mockPrograms } from '@mockData/mockProgramData'
import { waitFor, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { render } from 'wrappers/testUtil'
import ProgramsPage from 'app/mentorship/programs/page'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('hooks/useUpdateProgramStatus', () => ({
  useUpdateProgramStatus: () => ({ updateProgramStatus: jest.fn() }),
}))

describe('ProgramsPage Accessibility', () => {
  it('should have no accessibility violations', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockPrograms,
      totalPages: 1,
    })

    const { container } = render(<ProgramsPage />)

    await waitFor(() => {
      expect(screen.getByText('Program 1')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
