import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import MarkdownWrapper from 'components/MarkdownWrapper'

expect.extend(toHaveNoViolations)

jest.mock('markdown-it/index.mjs', () => {
  return jest.fn().mockImplementation(() => ({
    render: (content: string) => {
      // Very simple mock: replace **bold** and [link](url)
      return content
        .replaceAll(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replaceAll(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>')
    },
    use: jest.fn().mockReturnThis(),
  }))
})

describe('MarkdownWrapper a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<MarkdownWrapper content="test" className="custom-class" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
