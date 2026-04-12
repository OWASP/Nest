import { render, screen, fireEvent } from '@testing-library/react'
import { FormDateInput } from 'components/forms/shared/FormDateInput'

describe('FormDateInput Component', () => {
  const defaultProps = {
    id: 'test-date',
    label: 'Test Date',
    value: '2024-01-01',
    onValueChange: jest.fn(),
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders with required props', () => {
      render(<FormDateInput {...defaultProps} />)

      expect(screen.getByLabelText(/Test Date/)).toBeInTheDocument()
      expect(screen.getByLabelText(/Test Date/)).toHaveValue('2024-01-01')
      expect(screen.getByLabelText(/Test Date/)).toHaveAttribute('type', 'date')
    })

    it('renders with required true', () => {
      render(<FormDateInput {...defaultProps} required={true} />)

      expect(screen.getByLabelText(/Test Date/)).toBeRequired()
    })

    it('renders with required false (explicit)', () => {
      render(<FormDateInput {...defaultProps} required={false} />)

      expect(screen.getByLabelText(/Test Date/)).not.toBeRequired()
    })

    it('renders with required undefined (default)', () => {
      render(<FormDateInput {...defaultProps} required={undefined} />)

      expect(screen.getByLabelText(/Test Date/)).not.toBeRequired()
    })
  })

  describe('Validation', () => {
    it('shows error message when touched and error exists', () => {
      render(<FormDateInput {...defaultProps} touched={true} error="Invalid date" />)

      expect(screen.getByTestId('error-message')).toHaveTextContent('Invalid date')
      expect(screen.getByLabelText(/Test Date/)).toHaveAttribute('aria-invalid', 'true')
    })

    it('does not show error when not touched', () => {
      render(<FormDateInput {...defaultProps} touched={false} error="Invalid date" />)

      expect(screen.queryByTestId('error-message')).not.toBeInTheDocument()
      expect(screen.getByLabelText(/Test Date/)).toHaveAttribute('aria-invalid', 'false')
    })

    it('does not show error when touched but no error', () => {
      render(<FormDateInput {...defaultProps} touched={true} error="" />)

      expect(screen.queryByTestId('error-message')).not.toBeInTheDocument()
    })
  })

  describe('Interaction', () => {
    it('calls onValueChange when input changes', () => {
      render(<FormDateInput {...defaultProps} />)

      const input = screen.getByLabelText(/Test Date/)
      fireEvent.change(input, { target: { value: '2024-02-02' } })

      expect(defaultProps.onValueChange).toHaveBeenCalledWith('2024-02-02')
    })
  })

  describe('Constraints', () => {
    it('passes min and max props to input', () => {
      render(<FormDateInput {...defaultProps} min="2023-01-01" max="2025-01-01" />)

      const input = screen.getByLabelText(/Test Date/)
      expect(input).toHaveAttribute('min', '2023-01-01')
      expect(input).toHaveAttribute('max', '2025-01-01')
    })
  })

  describe('Styling and Structure', () => {
    it('renders with correct container classes', () => {
      const { container } = render(<FormDateInput {...defaultProps} />)

      const wrapper = container.firstChild as HTMLElement
      expect(wrapper).toHaveClass('w-full', 'min-w-0')
      expect(wrapper).toHaveStyle({ maxWidth: '100%', overflow: 'hidden' })
    })

    it('renders label element associated with input', () => {
      render(<FormDateInput {...defaultProps} />)

      const label = screen.getByText('Test Date')
      expect(label.tagName).toBe('LABEL')
      expect(label).toHaveAttribute('for', 'test-date')
    })

    it('renders input with correct styling classes', () => {
      render(<FormDateInput {...defaultProps} />)

      const input = screen.getByLabelText(/Test Date/)
      expect(input).toHaveClass('w-full', 'rounded-md')
    })
  })
})
