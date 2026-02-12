import { render, screen, fireEvent } from '@testing-library/react'
import { FormDateInput } from 'components/forms/shared/FormDateInput'

// Mock styles from imported component
jest.mock('components/forms/shared/FormDateInput', () => {
  const originalModule = jest.requireActual('components/forms/shared/FormDateInput')
  return {
    ...originalModule,
  }
})

// Mock @heroui/react Input component
jest.mock('@heroui/react', () => ({
  // eslint-disable-next-line @typescript-eslint/naming-convention
  Input: jest.fn(
    ({
      id,
      label,
      value,
      onValueChange,
      type,
      isRequired,
      isInvalid,
      errorMessage,
      min,
      max,
      labelPlacement,
      classNames,
    }) => (
      <div data-testid="mock-input-container">
        <label htmlFor={id}>{label}</label>
        <input
          id={id}
          type={type}
          value={value}
          onChange={(e) => onValueChange(e.target.value)}
          required={isRequired}
          min={min}
          max={max}
          aria-invalid={isInvalid}
          data-label-placement={labelPlacement}
          data-class-names={JSON.stringify(classNames)}
        />
        {errorMessage && <span data-testid="error-message">{errorMessage}</span>}
      </div>
    )
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
      expect(screen.getByLabelText('Test Date')).toHaveValue('2024-01-01')
      expect(screen.getByLabelText('Test Date')).toHaveAttribute('type', 'date')
    })

    it('renders with required true', () => {
      render(<FormDateInput {...defaultProps} required={true} />)

      expect(screen.getByLabelText('Test Date')).toBeRequired()
    })

    it('renders with required false (explicit)', () => {
      render(<FormDateInput {...defaultProps} required={false} />)

      expect(screen.getByLabelText('Test Date')).not.toBeRequired()
    })

    it('renders with required undefined (default)', () => {
      // This specifically targets the "required = false" default assignment
      render(<FormDateInput {...defaultProps} required={undefined} />)

      expect(screen.getByLabelText('Test Date')).not.toBeRequired()
    })
  })

  describe('Validation', () => {
    it('shows error message when touched and error exists', () => {
      render(<FormDateInput {...defaultProps} touched={true} error="Invalid date" />)

      expect(screen.getByTestId('error-message')).toHaveTextContent('Invalid date')
      expect(screen.getByLabelText('Test Date')).toHaveAttribute('aria-invalid', 'true')
    })

    it('does not show error when not touched', () => {
      render(<FormDateInput {...defaultProps} touched={false} error="Invalid date" />)

      expect(screen.queryByTestId('error-message')).not.toBeInTheDocument()
      expect(screen.getByLabelText('Test Date')).toHaveAttribute('aria-invalid', 'false')
    })

    it('does not show error when touched but no error', () => {
      render(<FormDateInput {...defaultProps} touched={true} error="" />)

      expect(screen.queryByTestId('error-message')).not.toBeInTheDocument()
    })
  })

  describe('Interaction', () => {
    it('calls onValueChange when input changes', () => {
      render(<FormDateInput {...defaultProps} />)

      const input = screen.getByLabelText('Test Date')
      fireEvent.change(input, { target: { value: '2024-02-02' } })

      expect(defaultProps.onValueChange).toHaveBeenCalledWith('2024-02-02')
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

      // The outer div in the component
      const wrapper = container.firstChild as HTMLElement
      expect(wrapper).toHaveClass('w-full', 'min-w-0')
      expect(wrapper).toHaveStyle({ maxWidth: '100%', overflow: 'hidden' })
    })

    it('passes common class names to Input', () => {
      render(<FormDateInput {...defaultProps} />)

      const input = screen.getByLabelText('Test Date')
      const classNames = JSON.parse(input.dataset.classNames || '{}')

      expect(classNames).toEqual(
        expect.objectContaining({
          base: 'w-full min-w-0',
          label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
          input: 'text-gray-800 dark:text-gray-200',
          inputWrapper: 'bg-gray-50 dark:bg-gray-800',
          helperWrapper: 'min-w-0 max-w-full w-full',
          errorMessage: 'break-words whitespace-normal max-w-full w-full',
        })
      )
    })

    it('sets label placement to outside', () => {
      render(<FormDateInput {...defaultProps} />)
      const input = screen.getByLabelText('Test Date')
      expect(input).toHaveAttribute('data-label-placement', 'outside')
    })
  })
})
