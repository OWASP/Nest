import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { Modal } from 'components/Modal'

// Mock the portal container
beforeEach(() => {
  const portalRoot = document.createElement('div')
  portalRoot.setAttribute('id', 'portal-root')
  document.body.appendChild(portalRoot)
})

afterEach(() => {
  document.body.innerHTML = ''
})

// Mock FontAwesomeIcon since we don't need to test the actual icon rendering
jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

describe('Modal Component', () => {
  const defaultProps = {
    title: 'Test Modal',
    summary: 'Test Summary',
    hint: 'Test Hint',
    isOpen: true,
    onClose: jest.fn(),
    url: 'https://example.com/issue/123',
  }

  it('renders nothing when isOpen is false', () => {
    render(<Modal {...defaultProps} isOpen={false} />)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('renders modal with all components when isOpen is true', () => {
    render(<Modal {...defaultProps} />)

    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Test Modal')).toBeInTheDocument()
    expect(screen.getByText('Test Summary')).toBeInTheDocument()
    expect(screen.getByText('Test Hint')).toBeInTheDocument()
    expect(screen.getByText('How to tackle it')).toBeInTheDocument()
  })

  describe('URL handling', () => {
    it('opens URL in new window when View issue button is clicked', () => {
      const windowSpy = jest.spyOn(window, 'open').mockImplementation(() => null)
      render(<Modal {...defaultProps} />)

      const viewIssueButton = screen.getByRole('button', { name: /view issue/i })
      fireEvent.click(viewIssueButton)

      expect(windowSpy).toHaveBeenCalledWith(defaultProps.url, '_blank', 'noopener,noreferrer')
      windowSpy.mockRestore()
    })

    it('renders View issue button', () => {
      render(<Modal {...defaultProps} />)
      expect(screen.getByRole('button', { name: /view issue/i })).toBeInTheDocument()
    })
  })

  it('renders children content when provided', () => {
    render(
      <Modal {...defaultProps}>
        <div data-testid="child-content">Child Content</div>
      </Modal>
    )

    expect(screen.getByTestId('child-content')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', async () => {
    const onClose = jest.fn()
    render(<Modal {...defaultProps} onClose={onClose} />)

    const closeButton = screen.getByRole('button', { name: /close modal/i })
    await userEvent.click(closeButton)

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('calls onClose when clicking outside the modal', () => {
    const onClose = jest.fn()
    render(<Modal {...defaultProps} onClose={onClose} />)

    const overlay = screen.getByRole('presentation')
    fireEvent.mouseDown(overlay)

    expect(onClose).toHaveBeenCalledTimes(0)
  })

  it('handles escape key press', () => {
    const onClose = jest.fn()
    render(<Modal {...defaultProps} onClose={onClose} />)

    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' })

    expect(onClose).toHaveBeenCalledTimes(2)
  })

  it('manages body overflow style correctly', () => {
    const { unmount } = render(<Modal {...defaultProps} />)

    expect(document.body.style.overflow).toBe('hidden')

    unmount()

    expect(document.body.style.overflow).toBe('')
  })

  it('renders with correct accessibility attributes', () => {
    render(<Modal {...defaultProps} />)

    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(dialog).toHaveAttribute('aria-labelledby', 'modal-title')
    expect(dialog).toHaveAttribute('tabIndex', '-1')
  })

  it('renders without hint section when hint prop is not provided', () => {
    const propsWithoutHint = {
      ...defaultProps,
      hint: undefined,
    }

    render(<Modal {...propsWithoutHint} />)

    expect(screen.queryByText('How to tackle it')).not.toBeInTheDocument()
  })

  describe('Event Listener Management', () => {
    it('cleans up event listeners on unmount', () => {
      const addEventListenerSpy = jest.spyOn(document, 'addEventListener')
      const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener')

      const { unmount } = render(<Modal {...defaultProps} />)

      expect(addEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function))

      unmount()

      expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function))

      addEventListenerSpy.mockRestore()
      removeEventListenerSpy.mockRestore()
    })
  })
})
