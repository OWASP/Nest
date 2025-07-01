import { render } from '@testing-library/react'
import * as nextNavigation from 'next/navigation'
import AutoScrollToTop from 'components/AutoScrollToTop'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

describe('AutoScrollToTop', () => {
  const originalScrollTo = window.scrollTo

  beforeEach(() => {
    window.scrollTo = jest.fn()
  })

  afterEach(() => {
    jest.clearAllMocks()
    window.scrollTo = originalScrollTo
  })

  it('calls window.scrollTo on mount', () => {
    ;(nextNavigation.usePathname as jest.Mock).mockReturnValue('/test-path')
    render(<AutoScrollToTop />)
    expect(window.scrollTo).toHaveBeenCalledWith(0, 0)
  })

  it('calls window.scrollTo when pathname changes', () => {
    let pathname = '/first'
    ;(nextNavigation.usePathname as jest.Mock).mockImplementation(() => pathname)
    const { rerender } = render(<AutoScrollToTop />)
    expect(window.scrollTo).toHaveBeenCalledTimes(1)

    pathname = '/second'
    rerender(<AutoScrollToTop />)
    expect(window.scrollTo).toHaveBeenCalledTimes(2)
  })
})
