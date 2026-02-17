import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import type { ProfilePageStructuredData } from 'types/profilePageStructuredData'
import StructuredDataScript from 'components/StructuredDataScript'

const mockData: ProfilePageStructuredData = {
  '@context': 'https://schema.org',
  '@type': 'ProfilePage',
  mainEntity: {
    '@type': 'Person',
    name: 'Test User',
    url: 'https://example.com/testuser',
    description: 'A test user profile',
    sameAs: ['https://github.com/testuser'],
  },
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('StructuredDataScript a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should have no accessibility violations', async () => {
    const { container } = render(<StructuredDataScript data={mockData} />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
