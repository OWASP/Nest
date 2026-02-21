import { useQuery } from '@apollo/client/react'
import { mockOrganizationDetailsData } from '@mockData/mockOrganizationData'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import OrganizationDetailsPage from 'app/organizations/[organizationKey]/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('OrganizationDetailsPage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
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
