import { faCheck } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import '@testing-library/jest-dom'
import DialogComp from 'components/Modal'

jest.mock('@/components/MarkdownWrapper', () => {
  return ({ content, className }: { content: string; className?: string }) => (
    <div
      data-testid="markdown"
      className={`md-wrapper ${className || ''}`}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  )
})

jest.mock('components/ActionButton', () => ({ children, onClick }) => (
  <button data-testid="action-button" onClick={onClick}>
    {children}
  </button>
))

describe('DialogComp', () => {
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
      icon: <FontAwesomeIcon icon={faCheck} />,
      url: 'https://example.com',
      onPress: mockOnClick,
    },
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })
  afterEach(() => {
    jest.clearAllMocks()
    jest.restoreAllMocks()
  })

  test('does not render when isOpen is false', async () => {
    render(<DialogComp {...defaultProps} isOpen={false} />)

    await waitFor(() => expect(screen.queryByText('Test Title')).not.toBeInTheDocument())
  })

  test('renders summary section correctly', async () => {
    render(<DialogComp {...defaultProps} />)

    await waitFor(() => expect(screen.getByText('Summary')).toBeInTheDocument())
  })

  test('renders hint section when hint prop is provided', async () => {
    render(<DialogComp {...defaultProps} />)

    await waitFor(() => expect(screen.getByText('How to tackle it')).toBeInTheDocument())
  })

  test('does not render hint section when hint prop is not provided', async () => {
    render(<DialogComp {...defaultProps} hint={undefined} />)

    await waitFor(() => expect(screen.queryByText('How to tackle it')).not.toBeInTheDocument())
  })

  test('renders children content when provided', async () => {
    render(
      <DialogComp {...defaultProps}>
        <div data-testid="child-content">Child Content</div>
      </DialogComp>
    )

    await waitFor(() => {
      expect(screen.getByTestId('child-content')).toBeInTheDocument()
      expect(screen.getByText('Child Content')).toBeInTheDocument()
    })
  })

  test('calls onClose when close button is clicked', async () => {
    render(<DialogComp {...defaultProps} />)

    const closeButton = screen.getByText('Close')
    fireEvent.click(closeButton)

    await waitFor(() => expect(mockOnClose).toHaveBeenCalledTimes(1))
  })
})
