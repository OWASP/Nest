import { render, screen } from '@testing-library/react'
import DOMPurify from 'dompurify'
import Markdown from 'components/MarkdownWrapper'

// Mock the external dependencies
jest.mock('dompurify')
jest.mock('markdown-it', () => {
  return jest.fn().mockImplementation(() => ({
    render: (content: string) => `<p>${content}</p>`,
  }))
})

describe('Markdown Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()

    // Setup DOMPurify mock to return the input
    ;(DOMPurify.sanitize as jest.Mock).mockImplementation((html) => html)
  })

  it('renders markdown content correctly', () => {
    const content = 'Hello World'
    render(<Markdown content={content} />)

    expect(screen.getByText('Hello World')).toBeInTheDocument()
  })

  it('applies custom className when provided', () => {
    const content = 'Test content'
    const { container } = render(<Markdown content={content} className="custom-class" />)

    expect(container.firstChild).toHaveClass('md-wrapper', 'custom-class')
  })

  it('sanitizes HTML content', () => {
    const content = '<script>alert("xss")</script>Hello'
    render(<Markdown content={content} />)

    expect(DOMPurify.sanitize).toHaveBeenCalledTimes(1)
    expect(DOMPurify.sanitize).toHaveBeenCalledWith('<p><script>alert("xss")</script>Hello</p>')
  })

  it('handles empty content', () => {
    render(<Markdown content="" />)

    expect(DOMPurify.sanitize).toHaveBeenCalledWith('<p></p>')
  })

  it('renders complex markdown with various elements', () => {
    const complexContent = `
# Heading
- List item 1
- List item 2

[Link](https://example.com)

\`\`\`
code block
\`\`\`
    `

    // Mock the markdown-it render for this specific test
    const mockHtml = `
      <h1>Heading</h1>
      <ul>
        <li>List item 1</li>
        <li>List item 2</li>
      </ul>
      <p><a href="https://example.com">Link</a></p>
      <pre><code>code block</code></pre>
    `

    jest.requireMock('markdown-it').mockImplementation(() => ({
      render: () => mockHtml,
    }))

    render(<Markdown content={complexContent} />)

    expect(DOMPurify.sanitize).toHaveBeenCalledWith(mockHtml)
  })

  it('preserves markdown-it configuration options', () => {
    const markdownIt = jest.requireMock('markdown-it')
    render(<Markdown content="test" />)

    expect(markdownIt).toHaveBeenCalledWith({
      html: true,
      linkify: true,
      typographer: true,
    })
  })
})
