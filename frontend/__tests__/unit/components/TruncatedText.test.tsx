import { render, screen } from 'wrappers/testUtil'
import { TruncatedText } from 'components/TruncatedText'

describe('Truncate Component', () => {
  const longText = 'This is very long text that should be truncated for display.'

  test('renders full text when shorter than maxLength', () => {
    render(<TruncatedText text="Short text" maxLength={40} />)
    expect(screen.getByText('Short text')).toBeInTheDocument()
  })

  test('truncates long text and adds ellipsis', () => {
    render(<TruncatedText text={longText} maxLength={40} />)
    expect(screen.getByText(/This is very long text that should be tr\.\.\./)).toBeInTheDocument()
  })

  test('does not truncate if disabledTooltip is true', () => {
    render(<TruncatedText text={longText} maxLength={40} disabledTooltip />)
    expect(screen.getByText(longText)).toBeInTheDocument()
  })
})
