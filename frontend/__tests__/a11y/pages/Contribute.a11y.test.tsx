import { mockContributeData } from '@mockData/mockContributeData'
import { screen, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import { render } from 'wrappers/testUtil'
import ContributePage from 'app/contribute/page'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

describe('ContributePage Accessibility', () => {
  it('should have no accessibility violations', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockContributeData.issues,
    })

    const { container } = render(<ContributePage />)

    await waitFor(() => {
      expect(screen.getByText('Contribution 1')).toBeInTheDocument()
    })
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
