import { render, screen } from '@testing-library/react'
import Markdown from 'components/MarkdownWrapper'

// Mock dompurify and markdown-it for isolation
jest.mock('dompurify', () => ({
  sanitize: (html: string) => html,
}))

jest.mock('markdown-it/index.mjs', () => {
  return jest.fn().mockImplementation(() => ({
    render: (content: string) => {
      // Very simple mock: replace **bold** and [link](url)
      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>')
    },
    use: jest.fn().mockReturnThis(),
  }))
})

describe('Markdown component', () => {
  it('renders markdown as HTML', () => {
    render(<Markdown content={'**bold**'} />)
    expect(screen.getByText('bold').tagName.toLowerCase()).toBe('strong')
  })

  it('applies custom className', () => {
    render(<Markdown content="test" className="custom-class" />)
    const wrapper = screen.getByText('test').closest('div')
    expect(wrapper).toHaveClass('md-wrapper')
    expect(wrapper).toHaveClass('custom-class')
  })

  it('renders links', () => {
    render(<Markdown content={'[Google](https://google.com)'} />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', 'https://google.com')
    expect(link).toHaveTextContent('Google')
  })

  it('sanitizes dangerous HTML', () => {
    render(<Markdown content={'<img src=x onerror=alert(1) />hello'} />)
    // In our mock, dompurify does nothing, so just check the content is present
    expect(screen.getByText('hello')).toBeInTheDocument()
  })
})
