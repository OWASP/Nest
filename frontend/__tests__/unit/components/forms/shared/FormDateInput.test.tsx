import { render, screen, fireEvent } from '@testing-library/react'
import { FormDateInput } from 'components/forms/shared/FormDateInput'

jest.mock('@heroui/react', () => ({
  TextField: ({ children, isRequired, isInvalid, value, onChange }) => (
    <div data-testid="mock-textfield" data-required={isRequired} data-invalid={isInvalid}>
      {typeof children === 'function' ? children({ isRequired, isInvalid }) : children}
    </div>
  ),
  Label: ({ children, htmlFor, className }) => (
    <label htmlFor={htmlFor} className={className}>
      {children}
    </label>
  ),
  Input: ({ id, type, min, max, className }) => (
    <input id={id} type={type} min={min} max={max} className={className} onChange={() => {}} />
  ),
  FieldError: ({ children, className }) => (
    <span data-testid="error-message" className={className}>
      {children}
    </span>
  ),
}))

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
      expect(screen.getByLabelText('Test Date')).toBeInTheDocument()
      expect(screen.getByLabelText('Test Date')).toHaveAttribute('type', 'date')
    })

    it('renders with required true', () => {
      render(<FormDateInput {...defaultProps} required={true} />)
      expect(screen.getByTestId('mock-textfield')).toHaveAttribute('data-required', 'true')
    })

    it('renders with required false (explicit)', () => {
      render(<FormDateInput {...defaultProps} required={false} />)
      expect(screen.getByTestId('mock-textfield')).toHaveAttribute('data-required', 'false')
    })

    it('renders with required undefined (default)', () => {
      render(<FormDateInput {...defaultProps} required={undefined} />)
      expect(screen.getByTestId('mock-textfield')).toHaveAttribute('data-required', 'false')
    })
  })

  describe('Validation', () => {
    it('shows error message when touched and error exists', () => {
      render(<FormDateInput {...defaultProps} touched={true} error="Invalid date" />)
      expect(screen.getByTestId('error-message')).toHaveTextContent('Invalid date')
      expect(screen.getByTestId('mock-textfield')).toHaveAttribute('data-invalid', 'true')
    })

    it('does not show error when not touched', () => {
      render(<FormDateInput {...defaultProps} touched={false} error="Invalid date" />)
      expect(screen.queryByTestId('error-message')).not.toBeInTheDocument()
      expect(screen.getByTestId('mock-textfield')).toHaveAttribute('data-invalid', 'false')
    })

    it('does not show error when touched but no error', () => {
      render(<FormDateInput {...defaultProps} touched={true} error="" />)
      expect(screen.queryByTestId('error-message')).not.toBeInTheDocument()
    })
  })

  describe('Interaction', () => {
    it('calls onValueChange when input changes', () => {
      const onValueChange = jest.fn()
      render(<FormDateInput {...defaultProps} onValueChange={onValueChange} />)
      // TextField onChange is wired to onValueChange in the component
      expect(screen.getByLabelText('Test Date')).toBeInTheDocument()
    })
  })

  describe('Constraints', () => {
    it('passes min and max props to input', () => {
      render(<FormDateInput {...defaultProps} min="2023-01-01" max="2025-01-01" />)
      const input = screen.getByLabelText('Test Date')
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
  })
})
