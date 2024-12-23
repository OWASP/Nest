import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { Modal } from '../../../src/components/Modal/Modal'
import '@testing-library/jest-dom'

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

    expect(onClose).toHaveBeenCalledTimes(1)
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

    expect(document.body.style.overflow).toBe('unset')
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

  it('applies dark mode classes correctly', () => {
    render(<Modal {...defaultProps} />)

    const modalContent = screen.getByRole('dialog')
    expect(modalContent).toHaveClass('dark:bg-[#1c1f24]')
    expect(modalContent).toHaveClass('dark:border-gray-800')
  })

  describe('Event Listener Management', () => {
    it('cleans up event listeners on unmount', () => {
      const addEventListenerSpy = jest.spyOn(document, 'addEventListener')
      const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener')

      const { unmount } = render(<Modal {...defaultProps} />)

      expect(addEventListenerSpy).toHaveBeenCalledWith('mousedown', expect.any(Function))

      unmount()

      expect(removeEventListenerSpy).toHaveBeenCalledWith('mousedown', expect.any(Function))

      addEventListenerSpy.mockRestore()
      removeEventListenerSpy.mockRestore()
    })
  })
})
