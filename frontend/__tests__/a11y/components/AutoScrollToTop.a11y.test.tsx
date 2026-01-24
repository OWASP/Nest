import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import AutoScrollToTop from 'components/AutoScrollToTop'

jest.mock('next/navigation', () => ({
  usePathname: () => '/test-path',
}))

beforeAll(() => {
  window.scrollTo = jest.fn()
})

afterAll(() => {
  jest.clearAllMocks()
})

describe('AutoScrollToTop Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<AutoScrollToTop />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
