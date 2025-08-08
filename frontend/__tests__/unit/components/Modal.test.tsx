import { faCheck } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
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

// Mock @heroui/modal components to avoid framer-motion issues
jest.mock('@heroui/modal', () => {
  return {
    Modal: ({ isOpen, children }: { isOpen: boolean; children: React.ReactNode }) =>
      isOpen ? <dialog open>{children}</dialog> : null,
    ModalContent: ({
      children,
      className,
      ...props
    }: React.PropsWithChildren<{ className?: string } & Record<string, unknown>>) => (
      <div className={className} {...props}>
        {children}
      </div>
    ),
    ModalHeader: ({
      children,
      className,
      ...props
    }: React.PropsWithChildren<{ className?: string } & Record<string, unknown>>) => (
      <header className={className} {...props}>
        {children}
      </header>
    ),
    ModalBody: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
      <div {...props}>{children}</div>
    ),
    ModalFooter: ({
      children,
      className,
      ...props
    }: React.PropsWithChildren<{ className?: string } & Record<string, unknown>>) => (
      <footer className={className} {...props}>
        {children}
      </footer>
    ),
  }
})

jest.mock('@heroui/button', () => ({
  Button: ({
    children,
    onPress,
    ...props
  }: React.PropsWithChildren<{ onPress?: () => void } & Record<string, unknown>>) => (
    <button onClick={onPress} {...props}>
      {children}
    </button>
  ),
}))

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

  it('does not render modal content when isOpen is false', () => {
    render(<DialogComp {...defaultProps} isOpen={false} />)
    expect(screen.queryByText('Test Title')).not.toBeInTheDocument()
  })

  it('renders modal with title and description correctly', () => {
    render(<DialogComp {...defaultProps} />)
    expect(screen.getByText('Test Title')).toBeInTheDocument()
    expect(screen.getByText('Test Description')).toBeInTheDocument()
  })

  it('renders summary section correctly', () => {
    render(<DialogComp {...defaultProps} />)
    expect(screen.getByText('Summary')).toBeInTheDocument()
    const markdownElements = screen.getAllByTestId('markdown')
    expect(markdownElements.length).toBeGreaterThan(0)
  })

  it('renders hint section when hint prop is provided', () => {
    render(<DialogComp {...defaultProps} />)
    expect(screen.getByText('How to tackle it')).toBeInTheDocument()
    const markdownElements = screen.getAllByTestId('markdown')
    expect(markdownElements).toHaveLength(2)
  })

  it('does not render hint section when hint prop is not provided', () => {
    render(<DialogComp {...defaultProps} hint={undefined} />)
    expect(screen.queryByText('How to tackle it')).not.toBeInTheDocument()
    const markdownElements = screen.getAllByTestId('markdown')
    expect(markdownElements).toHaveLength(1)
  })

  it('renders children content when provided', () => {
    render(
      <DialogComp {...defaultProps}>
        <div data-testid="child-content">Child Content</div>
      </DialogComp>
    )
    expect(screen.getByTestId('child-content')).toBeInTheDocument()
    expect(screen.getByText('Child Content')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    render(<DialogComp {...defaultProps} />)
    const closeButton = screen.getByRole('button', { name: /close/i })
    fireEvent.click(closeButton)
    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('renders action button when button prop is provided', () => {
    render(<DialogComp {...defaultProps} />)
    expect(screen.getByTestId('action-button')).toBeInTheDocument()
    expect(screen.getByText('Action')).toBeInTheDocument()
  })

  it('renders with minimal required props', () => {
    const minimalProps = {
      title: 'Minimal Title',
      summary: 'Minimal Summary',
      isOpen: true,
      onClose: mockOnClose,
      description: '',
      button: {
        label: 'Minimal Action',
        icon: null,
        url: '',
        onPress: mockOnClick,
      },
    }

    render(<DialogComp {...minimalProps} />)
    expect(screen.getByText('Minimal Title')).toBeInTheDocument()
    expect(screen.getByText('Summary')).toBeInTheDocument()
    expect(screen.getByText('Minimal Action')).toBeInTheDocument()
  })

  it('handles empty title, summary, description', () => {
    render(<DialogComp {...defaultProps} title="" summary="" description="" />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Summary')).toBeInTheDocument()
  })

  it('has correct accessibility attributes', () => {
    render(<DialogComp {...defaultProps} />)
    const modal = screen.getByRole('dialog')
    expect(modal).toBeInTheDocument()

    const closeButton = screen.getByText('Close')
    expect(closeButton).toHaveAttribute('aria-label', 'close-modal')
  })

  it('renders important classNames and DOM structure', () => {
    render(<DialogComp {...defaultProps} />)
    expect(document.querySelector('.animate-scaleIn')).toBeInTheDocument()
    expect(document.querySelector('.font-bold')).toBeInTheDocument()
    expect(document.querySelector('.flex.justify-end')).toBeInTheDocument()
  })

  it('handles null hint prop', () => {
    render(<DialogComp {...defaultProps} hint={null} />)
    expect(screen.getByText('Summary')).toBeInTheDocument()
    expect(screen.queryByText('How to tackle it')).not.toBeInTheDocument()
  })

  it('renders markdown content correctly', () => {
    const markdownContent = '**Bold text** and *italic text*'

    render(<DialogComp {...defaultProps} summary={markdownContent} hint={markdownContent} />)

    const markdownElements = screen.getAllByTestId('markdown')
    expect(markdownElements).toHaveLength(2)

    markdownElements.forEach((element) => {
      expect(element).toHaveClass('md-wrapper')
    })
  })
})
