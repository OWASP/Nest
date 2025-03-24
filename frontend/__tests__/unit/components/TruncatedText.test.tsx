import { render, screen } from 'wrappers/testUtil'
import { TruncatedText } from 'components/TruncatedText'

beforeAll(() => {
  global.ResizeObserver = class {
    observe = jest.fn()
    unobserve = jest.fn()
    disconnect = jest.fn()
  } as unknown as typeof ResizeObserver
})

describe('TruncatedText Component', () => {
  const longText = 'This is very long text that should be truncated for display.'

  test('renders full text when it fits within the container', () => {
    render(<TruncatedText text="Short text" className="w-auto" />)
    const textElement = screen.getByText('Short text')
    expect(textElement).toBeInTheDocument()
    expect(textElement).toHaveAttribute('title', 'Short text')
  })

  test('title attribute is always present', () => {
    render(<TruncatedText text={longText} />)
    const textElement = screen.getByText(longText)
    expect(textElement).toHaveAttribute('title', longText)
  })
})
