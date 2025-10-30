import { render, fireEvent, waitFor } from '@testing-library/react'
import ScrollToTop from 'components/ScrollToTop'

describe('ScrollToTop component test', () => {
  beforeEach(() => {
    globalThis.scrollTo = jest.fn()
    Object.defineProperty(globalThis, 'scrollY', { value: 0, writable: true })
    Object.defineProperty(globalThis, 'innerHeight', { value: 1000, writable: true })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('Initially, the button should be hidden', () => {
    const { getByLabelText } = render(<ScrollToTop />)
    const button = getByLabelText(/scroll to top/i)

    expect(button).toHaveClass('opacity-0')
    expect(button).toHaveClass('pointer-events-none')
  })

  test('The button should become visible after scrolling past the threshold', async () => {
    const { getByLabelText } = render(<ScrollToTop />)
    const button = getByLabelText(/scroll to top/i)

    Object.defineProperty(globalThis, 'scrollY', { value: 400, writable: true })
    globalThis.dispatchEvent(new Event('scroll'))

    await waitFor(() => {
      expect(button).toHaveClass('opacity-100')
      expect(button).toHaveClass('pointer-events-auto')
    })
  })

  test('Clicking the button should call window.scrollTo with smooth behavior', async () => {
    const { getByLabelText } = render(<ScrollToTop />)
    const button = getByLabelText(/scroll to top/i)

    Object.defineProperty(globalThis, 'scrollY', { value: 400, writable: true })
    globalThis.dispatchEvent(new Event('scroll'))

    await waitFor(() => {
      expect(button).toHaveClass('opacity-100')
    })

    fireEvent.click(button)
    expect(globalThis.scrollTo).toHaveBeenCalledWith({ top: 0, behavior: 'smooth' })
  })
})
