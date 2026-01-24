import { useQuery } from '@apollo/client/react'
import { mockOrganizationDetailsData } from '@mockData/mockOrganizationData'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import OrganizationDetailsPage from 'app/organizations/[organizationKey]/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

describe('OrganizationDetailsPage Accessibility', () => {
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockOrganizationDetailsData,
      loading: false,
      error: null,
    })

    const { container } = render(<OrganizationDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
