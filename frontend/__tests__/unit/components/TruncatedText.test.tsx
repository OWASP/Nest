import { render, screen } from 'wrappers/testUtil'
import { TruncatedText } from 'components/TruncatedText'

describe('TruncatedText Component', () => {
  const longText = 'This is very long text that should be truncated for display.'

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
})
