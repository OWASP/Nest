import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { FaCheck } from 'react-icons/fa6'
import Modal from 'components/Modal'

jest.mock('@/components/MarkdownWrapper', () => {
  return ({ content, className }: { content: string; className?: string }) => (
    <div
      data-testid="markdown"
      className={`md-wrapper ${className || ''}`}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  )
})

const mockOnClose = jest.fn()
const mockOnClick = jest.fn()

const defaultProps = {
  title: 'Test Title',
  summary: 'Test Summary',
  hint: 'Test Hint',
  description: 'Test Description',
  isOpen: true,
  onClose: mockOnClose,
  button: {
    label: 'Action',
    icon: <FaCheck data-testid="fa-check-icon" />,
    url: 'https://example.com',
    onPress: mockOnClick,
  },
}

describe('Modal a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Modal {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
