import { mockOrganizationData } from '@mockData/mockOrganizationData'
import { screen, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import { render } from 'wrappers/testUtil'
import Organization from 'app/organizations/page'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

describe('Organization Accessibility', () => {
  it('should have no accessibility violations', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockOrganizationData.hits,
    })

    const { container } = render(<Organization />)

    await waitFor(() => {
      expect(screen.getByText('Test Organization')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
