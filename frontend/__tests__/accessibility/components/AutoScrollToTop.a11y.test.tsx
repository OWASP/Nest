import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import AutoScrollToTop from 'components/AutoScrollToTop'

beforeAll(() => {
  window.scrollTo = jest.fn()
})

afterAll(() => {
  jest.clearAllMocks()
})

expect.extend(toHaveNoViolations)

describe('AutoScrollToTop Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<AutoScrollToTop />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
