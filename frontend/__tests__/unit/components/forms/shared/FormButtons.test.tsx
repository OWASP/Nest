import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import { FormButtons } from 'components/forms/shared/FormButtons'

const mockBack = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    back: mockBack,
  }),
}))

jest.mock('@heroui/button', () => ({
  Button: ({
    children,
    type,
    variant,
    onPress,
    isDisabled,
    color,
    className,
  }: {
    children: React.ReactNode
    type?: string
    variant?: string
    onPress?: () => void
    isDisabled?: boolean
    color?: string
    className?: string
  }) => (
    <button
      type={type as 'button' | 'submit' | 'reset' | undefined}
      onClick={onPress}
      disabled={isDisabled}
      data-variant={variant}
      data-color={color}
      className={className}
    >
      {children}
    </button>
  ),
}))

describe('FormButtons Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Renders successfully with minimal required props', () => {
    it('renders with loading false', () => {
      render(<FormButtons loading={false} />)

      expect(screen.getByText('Cancel')).toBeInTheDocument()
      expect(screen.getByText('Save')).toBeInTheDocument()
    })

    it('renders with loading true', () => {
      render(<FormButtons loading={true} />)

      expect(screen.getByText('Cancel')).toBeInTheDocument()
      expect(screen.getByText('Saving...')).toBeInTheDocument()
    })
  })

  describe('Prop-based behavior', () => {
    it('uses default submitText "Save" when not provided', () => {
      render(<FormButtons loading={false} />)

      expect(screen.getByText('Save')).toBeInTheDocument()
    })

    it('uses custom submitText when provided', () => {
      render(<FormButtons loading={false} submitText="Create" />)

      expect(screen.getByText('Create')).toBeInTheDocument()
      expect(screen.queryByText('Save')).not.toBeInTheDocument()
    })

    it('shows "Saving..." when loading regardless of submitText', () => {
      render(<FormButtons loading={true} submitText="Create" />)

      expect(screen.getByText('Saving...')).toBeInTheDocument()
      expect(screen.queryByText('Create')).not.toBeInTheDocument()
    })

    it('disables submit button when loading is true', () => {
      render(<FormButtons loading={true} />)

      const submitButton = screen.getByText('Saving...')
      expect(submitButton).toBeDisabled()
    })

    it('enables submit button when loading is false', () => {
      render(<FormButtons loading={false} />)

      const submitButton = screen.getByText('Save')
      expect(submitButton).not.toBeDisabled()
    })
  })

  describe('Event handling', () => {
    it('calls router.back when Cancel is clicked and no onCancel provided', () => {
      render(<FormButtons loading={false} />)

      const cancelButton = screen.getByText('Cancel')
      fireEvent.click(cancelButton)

      expect(mockBack).toHaveBeenCalledTimes(1)
    })

    it('calls onCancel when Cancel is clicked and onCancel is provided', () => {
      const mockOnCancel = jest.fn()
      render(<FormButtons loading={false} onCancel={mockOnCancel} />)

      const cancelButton = screen.getByText('Cancel')
      fireEvent.click(cancelButton)

      expect(mockOnCancel).toHaveBeenCalledTimes(1)
      expect(mockBack).not.toHaveBeenCalled()
    })

    it('does not call router.back when onCancel is provided', () => {
      const mockOnCancel = jest.fn()
      render(<FormButtons loading={false} onCancel={mockOnCancel} />)

      const cancelButton = screen.getByText('Cancel')
      fireEvent.click(cancelButton)

      expect(mockBack).not.toHaveBeenCalled()
    })
  })

  describe('Button types and variants', () => {
    it('Cancel button has type="button"', () => {
      render(<FormButtons loading={false} />)

      const cancelButton = screen.getByText('Cancel')
      expect(cancelButton).toHaveAttribute('type', 'button')
    })

    it('Submit button has type="submit"', () => {
      render(<FormButtons loading={false} />)

      const submitButton = screen.getByText('Save')
      expect(submitButton).toHaveAttribute('type', 'submit')
    })

    it('Cancel button has bordered variant', () => {
      render(<FormButtons loading={false} />)

      const cancelButton = screen.getByText('Cancel')
      expect(cancelButton).toHaveAttribute('data-variant', 'bordered')
    })

    it('Submit button has primary color', () => {
      render(<FormButtons loading={false} />)

      const submitButton = screen.getByText('Save')
      expect(submitButton).toHaveAttribute('data-color', 'primary')
    })
  })

  describe('DOM structure / classNames / styles', () => {
    it('renders container with correct classes', () => {
      const { container } = render(<FormButtons loading={false} />)

      const outerDiv = container.firstChild
      expect(outerDiv).toHaveClass('border-t', 'border-gray-200', 'pt-8')
    })

    it('renders button container with flex layout', () => {
      const { container } = render(<FormButtons loading={false} />)

      const buttonContainer = container.querySelector('.flex.flex-col')
      expect(buttonContainer).toBeInTheDocument()
    })

    it('buttons have font-medium class', () => {
      render(<FormButtons loading={false} />)

      const cancelButton = screen.getByText('Cancel')
      const submitButton = screen.getByText('Save')

      expect(cancelButton).toHaveClass('font-medium')
      expect(submitButton).toHaveClass('font-medium')
    })
  })

  describe('Edge cases', () => {
    it('handles empty submitText gracefully', () => {
      render(<FormButtons loading={false} submitText="" />)

      // When submitText is empty string, it should render empty (falsy in ternary)
      const buttons = screen.getAllByRole('button')
      expect(buttons).toHaveLength(2)
    })

    it('handles rapid clicking on cancel button', () => {
      const mockOnCancel = jest.fn()
      render(<FormButtons loading={false} onCancel={mockOnCancel} />)

      const cancelButton = screen.getByText('Cancel')

      fireEvent.click(cancelButton)
      fireEvent.click(cancelButton)
      fireEvent.click(cancelButton)

      expect(mockOnCancel).toHaveBeenCalledTimes(3)
    })

    it('cancel button works when submit is loading', () => {
      const mockOnCancel = jest.fn()
      render(<FormButtons loading={true} onCancel={mockOnCancel} />)

      const cancelButton = screen.getByText('Cancel')
      fireEvent.click(cancelButton)

      expect(mockOnCancel).toHaveBeenCalledTimes(1)
    })
  })

  describe('Accessibility', () => {
    it('all buttons are accessible by role', () => {
      render(<FormButtons loading={false} />)

      const buttons = screen.getAllByRole('button')
      expect(buttons).toHaveLength(2)
    })

    it('disabled state is properly set on submit button when loading', () => {
      render(<FormButtons loading={true} />)

      const submitButton = screen.getByText('Saving...')
      expect(submitButton).toHaveAttribute('disabled')
    })
  })
})
