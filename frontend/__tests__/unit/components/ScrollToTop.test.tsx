import { render, fireEvent, waitFor, act } from '@testing-library/react'
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

  test('Clicking the button should call globalThis.scrollTo with smooth behavior', async () => {
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

  test('The button should be hidden when scrolling back below the threshold', async () => {
    const { getByLabelText } = render(<ScrollToTop />)
    const button = getByLabelText(/scroll to top/i)

    // Scroll past threshold
    Object.defineProperty(globalThis, 'scrollY', { value: 400, writable: true })
    globalThis.dispatchEvent(new Event('scroll'))

    await waitFor(() => {
      expect(button).toHaveClass('opacity-100')
    })

    // Scroll back below threshold
    Object.defineProperty(globalThis, 'scrollY', { value: 100, writable: true })
    globalThis.dispatchEvent(new Event('scroll'))

    await waitFor(() => {
      expect(button).toHaveClass('opacity-0')
      expect(button).toHaveClass('pointer-events-none')
    })
  })

  test('Should clear pending scroll timeout when component unmounts', async () => {
    jest.useFakeTimers()
    const clearTimeoutSpy = jest.spyOn(globalThis, 'clearTimeout')

    const { unmount } = render(<ScrollToTop />)

    // Trigger a scroll event to set a timeout
    Object.defineProperty(globalThis, 'scrollY', { value: 400, writable: true })
    globalThis.dispatchEvent(new Event('scroll'))

    // Unmount before the timeout completes
    unmount()

    expect(clearTimeoutSpy).toHaveBeenCalled()
    clearTimeoutSpy.mockRestore()
    jest.useRealTimers()
  })

  test('Should throttle repeated scroll events', () => {
    jest.useFakeTimers()
    const setTimeoutSpy = jest.spyOn(globalThis, 'setTimeout')

    render(<ScrollToTop />)

    // First scroll event - should set a timeout
    Object.defineProperty(globalThis, 'scrollY', { value: 400, writable: true })
    globalThis.dispatchEvent(new Event('scroll'))

    expect(setTimeoutSpy).toHaveBeenCalledTimes(1)

    // Immediate second scroll event - should NOT set a new timeout due to throttling
    globalThis.dispatchEvent(new Event('scroll'))

    expect(setTimeoutSpy).toHaveBeenCalledTimes(1) // Still 1

    // Fast forward time to clear the timeout
    act(() => {
      jest.advanceTimersByTime(100)
    })

    // Third scroll event - should set a new timeout now
    globalThis.dispatchEvent(new Event('scroll'))
    expect(setTimeoutSpy).toHaveBeenCalledTimes(2)

    setTimeoutSpy.mockRestore()
    jest.useRealTimers()
  })
})
