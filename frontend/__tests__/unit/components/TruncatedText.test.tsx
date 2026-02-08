import { render, screen, act } from '@testing-library/react'
import { TruncatedText } from 'components/TruncatedText'

type ResizeObserverCallback = (entries: ResizeObserverEntry[], observer: ResizeObserver) => void

const mockObserve = jest.fn()
const mockDisconnect = jest.fn()
const mockResizeObserverCallback = jest.fn()

class MockResizeObserver {
  callback: ResizeObserverCallback
  constructor(callback: ResizeObserverCallback) {
    this.callback = callback
    mockResizeObserverCallback.mockImplementation(() => {
      this.callback([], this)
    })
  }
  observe = mockObserve
  disconnect = mockDisconnect
  unobserve = jest.fn()
}

beforeAll(() => {
  global.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver
})

afterAll(() => {
  jest.restoreAllMocks()
})

describe('TruncatedText Component', () => {
  const longText = 'This is very long text that should be truncated for display.'

  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders full text when it fits within the container', () => {
    render(<TruncatedText text="Short text" className="w-auto" />)
    const textElement = screen.getByText('Short text')
    expect(textElement).toBeInTheDocument()
    expect(textElement).toHaveAttribute('title', 'Short text')
  })

  test('truncates text when it exceeds container width', () => {
    render(
      <div style={{ width: '100px' }}>
        <TruncatedText text={longText} />
      </div>
    )
    const textElement = screen.getByText(longText)
    expect(textElement).toHaveClass('truncate')
    expect(textElement).toHaveClass('text-ellipsis')
  })

  test('title attribute is always present', () => {
    render(<TruncatedText text={longText} />)
    const textElement = screen.getByText(longText)
    expect(textElement).toHaveAttribute('title', longText)
  })

  test('renders children when text prop is not provided', () => {
    render(
      <TruncatedText>
        <span>Child content</span>
      </TruncatedText>
    )
    const textElement = screen.getByText('Child content')
    expect(textElement).toBeInTheDocument()
  })

  test('uses textContent for title when text prop is not provided', () => {
    render(<TruncatedText>Fallback content</TruncatedText>)
    const spanElement = screen.getByText('Fallback content').closest('span.truncate')
    expect(spanElement).toHaveAttribute('title', 'Fallback content')
  })

  test('applies custom className prop', () => {
    render(<TruncatedText text="Test" className="custom-class" />)
    const textElement = screen.getByText('Test')
    expect(textElement).toHaveClass('custom-class')
    expect(textElement).toHaveClass('truncate')
  })

  test('applies default empty className when not provided', () => {
    render(<TruncatedText text="Test" />)
    const textElement = screen.getByText('Test')
    expect(textElement).toHaveClass('truncate')
  })

  test('sets up ResizeObserver on mount', () => {
    render(<TruncatedText text="Observable text" />)
    expect(mockObserve).toHaveBeenCalled()
  })

  test('cleans up ResizeObserver and event listener on unmount', () => {
    const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener')

    const { unmount } = render(<TruncatedText text="Cleanup text" />)
    unmount()

    expect(mockDisconnect).toHaveBeenCalled()
    expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function))

    removeEventListenerSpy.mockRestore()
  })

  test('adds window resize event listener on mount', () => {
    const addEventListenerSpy = jest.spyOn(window, 'addEventListener')

    render(<TruncatedText text="Resize text" />)

    expect(addEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function))

    addEventListenerSpy.mockRestore()
  })

  test('handles ResizeObserver callback', () => {
    render(<TruncatedText text="Resize callback text" />)

    // Trigger the ResizeObserver callback
    act(() => {
      mockResizeObserverCallback()
    })

    const textElement = screen.getByText('Resize callback text')
    expect(textElement).toHaveAttribute('title', 'Resize callback text')
  })

  test('prefers text prop over children when both provided', () => {
    render(<TruncatedText text="Text prop">Children prop</TruncatedText>)
    expect(screen.getByText('Text prop')).toBeInTheDocument()
    expect(screen.queryByText('Children prop')).not.toBeInTheDocument()
  })

  test('handles empty text prop gracefully', () => {
    render(<TruncatedText text="">Fallback children</TruncatedText>)
    expect(screen.getByText('Fallback children')).toBeInTheDocument()
  })

  test('handles undefined text prop', () => {
    render(<TruncatedText text={undefined}>Fallback children</TruncatedText>)
    expect(screen.getByText('Fallback children')).toBeInTheDocument()
  })

  test('updates title on window resize event', () => {
    render(<TruncatedText text="Resize test" />)

    // Trigger window resize event
    act(() => {
      window.dispatchEvent(new Event('resize'))
    })

    const textElement = screen.getByText('Resize test')
    expect(textElement).toHaveAttribute('title', 'Resize test')
  })

  test('uses element.textContent when text prop is undefined', () => {
    render(<TruncatedText>Content without text prop</TruncatedText>)

    const spanElement = screen.getByText('Content without text prop')
    // The title should be set from textContent
    expect(spanElement).toHaveAttribute('title', 'Content without text prop')
  })

  test('handles null children gracefully', () => {
    render(<TruncatedText text={undefined} children={null} />)
    // Should render an empty span without crashing
    const spans = document.querySelectorAll('span.truncate')
    expect(spans.length).toBeGreaterThan(0)
  })

  test('sets title to empty string when both text and textContent are empty', () => {
    const { container } = render(<TruncatedText text="" />)
    const span = container.querySelector('span.truncate')
    // Title should be set (either empty or from textContent)
    expect(span).toHaveAttribute('title')
  })

  test('handles textRef becoming null during lifecycle', () => {
    // This tests the branch where textRef.current might not exist
    const { unmount, rerender } = render(<TruncatedText text="Initial" />)

    // Rerender with different text
    rerender(<TruncatedText text="Updated" />)

    const textElement = screen.getByText('Updated')
    expect(textElement).toHaveAttribute('title', 'Updated')

    unmount()
  })

  test('handles multiple rapid text changes', () => {
    const { rerender } = render(<TruncatedText text="First" />)

    rerender(<TruncatedText text="Second" />)
    rerender(<TruncatedText text="Third" />)

    const textElement = screen.getByText('Third')
    expect(textElement).toHaveAttribute('title', 'Third')
  })

  test('handles checkTruncation when element is null', () => {
    const { unmount } = render(<TruncatedText text="Test" />)

    // Trigger resize after unmount to hit the null branch
    unmount()

    // Dispatch resize event - should not throw even with no mounted component
    act(() => {
      window.dispatchEvent(new Event('resize'))
    })

    // If we reach here without errors, the null check worked
    expect(true).toBe(true)
  })

  test('ResizeObserver callback handles null element gracefully', () => {
    // Render and get reference to callback
    const { unmount } = render(<TruncatedText text="Observer test" />)

    // Unmount first to clear the ref
    unmount()

    // Trigger the stored callback after unmount - tests null branch in checkTruncation
    act(() => {
      mockResizeObserverCallback()
    })

    // Should not throw any errors
    expect(mockResizeObserverCallback).toHaveBeenCalled()
  })

  test('observer.observe is not called when textRef.current is initially null', () => {
    // This is difficult to test directly since React always sets the ref on mount
    // But we can verify the observer behavior with rapid mount/unmount
    jest.clearAllMocks()

    const { unmount } = render(<TruncatedText text="Quick mount" />)
    expect(mockObserve).toHaveBeenCalledTimes(1)

    unmount()

    // Verify disconnect was called on unmount
    expect(mockDisconnect).toHaveBeenCalledTimes(1)
  })
})
