import { render, screen } from 'wrappers/testUtil'
import { TruncatedText } from 'components/TruncatedText'

describe('TruncatedText Component', () => {
  const longText = 'This is very long text that should be truncated for display.'

  test('renders full text when it fits within container', () => {
    render(<TruncatedText text="Short text" className="w-auto" />)
    expect(screen.getByText('Short text')).toBeInTheDocument()
  })

  test('truncates long text with ellipsis dynamically', () => {
    render(<TruncatedText text={longText} className="w-20" />)
    const textElement = screen.getByText(/This is very long text that should be/)
    expect(textElement).toHaveClass('truncate')
  })

  test('shows tooltip when text is truncated', async () => {
    render(<TruncatedText text={longText} className="w-20" />)
    const textElement = screen.getByText(/This is very long text that should be/)
    textElement.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }))
    expect(await screen.findByRole('tooltip')).toBeInTheDocument()
  })

  test('does not show tooltip when text is fully visible', () => {
    render(<TruncatedText text={longText} className="w-full" disabledTooltip />)
    expect(screen.getByText(longText)).toBeInTheDocument()
  })

  test('renders correctly across different screen sizes', () => {
    render(<TruncatedText text={longText} className="max-w-xs sm:max-w-md md:max-w-lg" />)
    const textElement = screen.getByText(/This is very long text that should be/)
    expect(textElement).toHaveClass('truncate')
  })
})
