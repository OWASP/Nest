import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import React from 'react'
import GlobalSearch from 'components/GlobalSearch'

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
  })),
}))

jest.mock('@next/third-parties/google', () => ({
  sendGAEvent: jest.fn(),
}))

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('lodash', () => ({
  debounce: jest.fn((fn: (...args: unknown[]) => unknown) => {
    const debouncedFn = (...args: unknown[]) => fn(...args)
    debouncedFn.cancel = jest.fn()
    return debouncedFn
  }),
}))

jest.mock('react-icons/fa', () => ({
  FaSearch: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-search-icon" {...props} />
  ),
  FaTimes: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="fa-times-icon" {...props} />,
}))

jest.mock('react-icons/fa6', () => ({
  FaUser: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="fa-user-icon" {...props} />,
  FaCalendar: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-calendar-icon" {...props} />
  ),
  FaFolder: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-folder-icon" {...props} />
  ),
  FaBuilding: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-building-icon" {...props} />
  ),
  FaLocationDot: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="fa-location-icon" {...props} />
  ),
}))

jest.mock('react-icons/si', () => ({
  SiAlgolia: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="si-algolia-icon" {...props} />
  ),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('GlobalSearch a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  it('should have no accessibility violations', async () => {
    const { container } = render(
      <main>
        <GlobalSearch />
      </main>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
