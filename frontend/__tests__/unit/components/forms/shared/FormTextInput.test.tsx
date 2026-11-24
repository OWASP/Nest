import { fireEvent, render, screen } from '@testing-library/react'
import { FormTextInput } from 'components/forms/shared/FormTextInput'

jest.mock('@heroui/react', () => ({
  // eslint-disable-next-line @typescript-eslint/naming-convention
  Input: jest.fn(
    ({
      id,
      label,
      value,
      onValueChange,
      isInvalid,
      errorMessage,
      maxLength,
      'aria-describedby': ariaDescribedBy,
    }: {
      id: string
      label: string
      value: string
      onValueChange: (value: string) => void
      isInvalid?: boolean
      errorMessage?: string
      maxLength?: number
      'aria-describedby'?: string
    }) => (
      <div>
        <label htmlFor={id}>{label}</label>
        <input
          id={id}
          value={value}
          maxLength={maxLength}
          aria-invalid={isInvalid}
          aria-describedby={ariaDescribedBy}
          onChange={(e) => onValueChange(e.target.value)}
        />
        {errorMessage && <span>{errorMessage}</span>}
      </div>
    )
  ),
}))

describe('FormTextInput', () => {
  const defaultProps = {
    id: 'test-input',
    label: 'Test Label',
    value: '',
    onValueChange: jest.fn(),
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders the input and forwards value changes', () => {
    render(<FormTextInput {...defaultProps} />)

    fireEvent.change(screen.getByLabelText('Test Label'), { target: { value: 'abc' } })

    expect(defaultProps.onValueChange).toHaveBeenCalledWith('abc')
  })

  it('shows the error message only when touched', () => {
    const { rerender } = render(<FormTextInput {...defaultProps} error="Required" />)
    expect(screen.queryByText('Required')).not.toBeInTheDocument()

    rerender(<FormTextInput {...defaultProps} error="Required" touched />)
    expect(screen.getByText('Required')).toBeInTheDocument()
  })

  it('hides the counter without showCharCount', () => {
    render(<FormTextInput {...defaultProps} value="Hello" maxLength={50} />)

    expect(screen.queryByText(/characters/)).not.toBeInTheDocument()
    expect(screen.getByLabelText('Test Label')).not.toHaveAttribute('aria-describedby')
  })

  it('hides the counter when maxLength is not set', () => {
    render(<FormTextInput {...defaultProps} value="Hello" showCharCount />)

    expect(screen.queryByText(/characters/)).not.toBeInTheDocument()
  })

  it('renders the counter with the default color below the near-limit threshold', () => {
    render(<FormTextInput {...defaultProps} value="Hello" maxLength={50} showCharCount />)

    const counter = screen.getByText(/5\/50 characters/)
    expect(counter).toHaveClass('text-gray-400')
    expect(counter).not.toHaveClass('text-amber-500', 'text-red-500')
    expect(screen.queryByText(/limit reached/)).not.toBeInTheDocument()
  })

  it('uses the near-limit color within 10 characters of the limit', () => {
    render(<FormTextInput {...defaultProps} value={'a'.repeat(40)} maxLength={50} showCharCount />)

    const counter = screen.getByText(/40\/50 characters/)
    expect(counter).toHaveClass('text-amber-500')
    expect(screen.queryByText(/limit reached/)).not.toBeInTheDocument()
  })

  it('uses the at-limit color and label when the limit is reached', () => {
    render(<FormTextInput {...defaultProps} value={'a'.repeat(50)} maxLength={50} showCharCount />)

    const counter = screen.getByText(/50\/50 characters/)
    expect(counter).toHaveClass('text-red-500')
    expect(screen.getByText(/limit reached/)).toBeInTheDocument()
  })

  it('links the counter to the input for assistive technology', () => {
    render(<FormTextInput {...defaultProps} value="Hello" maxLength={50} showCharCount />)

    const counter = screen.getByText(/5\/50 characters/)
    expect(counter).toHaveAttribute('id', 'test-input-char-count')
    // No live region: announcing the count on every keystroke is noisy.
    expect(counter).not.toHaveAttribute('aria-live')
    expect(screen.getByLabelText('Test Label')).toHaveAttribute(
      'aria-describedby',
      'test-input-char-count'
    )
  })
})
