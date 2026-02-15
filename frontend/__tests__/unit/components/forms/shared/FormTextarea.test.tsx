import { render, screen, fireEvent } from '@testing-library/react'
import { FormTextarea } from 'components/forms/shared/FormTextarea'

describe('FormTextarea', () => {
  const defaultProps = {
    id: 'test-textarea',
    label: 'Test Label',
    placeholder: 'Enter text',
    value: '',
    onChange: jest.fn(),
  }

  it('renders with default props (required=false, rows=4)', () => {
    render(<FormTextarea {...defaultProps} />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toBeInTheDocument()
    // Check default rows
    expect(textarea).toHaveAttribute('rows', '4')
    // Check default required (should be false, so not required)
    expect(textarea).not.toBeRequired()
    // Check label logic for not required (no asterisk)
    expect(screen.queryByText('*')).not.toBeInTheDocument()
  })

  it('renders with required=true', () => {
    render(<FormTextarea {...defaultProps} required={true} />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toBeRequired()
    // Check label logic for required (asterisk present)
    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('renders with custom rows', () => {
    render(<FormTextarea {...defaultProps} rows={10} />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveAttribute('rows', '10')
  })

  it('renders error message and styles when touched and error exists', () => {
    const errorMsg = 'This field is required'
    render(<FormTextarea {...defaultProps} touched={true} error={errorMsg} />)
    expect(screen.getByText(errorMsg)).toBeInTheDocument()
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveClass('border-red-500')
    expect(textarea).toHaveClass('dark:border-red-500')
  })

  it('does not render error message when not touched', () => {
    render(<FormTextarea {...defaultProps} touched={false} error="Error" />)
    expect(screen.queryByText('Error')).not.toBeInTheDocument()
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveClass('border-gray-300')
  })

  it('calls onChange handler when typed into', () => {
    const handleChange = jest.fn()
    render(<FormTextarea {...defaultProps} onChange={handleChange} />)
    const textarea = screen.getByRole('textbox')
    fireEvent.change(textarea, { target: { value: 'New Value' } })
    expect(handleChange).toHaveBeenCalledTimes(1)
  })
})
