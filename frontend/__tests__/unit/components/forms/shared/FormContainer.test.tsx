import { render, screen, fireEvent } from '@testing-library/react'
import { FormContainer } from 'components/forms/shared/FormContainer'

describe('FormContainer', () => {
  const mockOnSubmit = jest.fn()
  const defaultProps = {
    title: 'Test Form',
    onSubmit: mockOnSubmit,
    children: <div>Form Content</div>,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders with required props', () => {
    render(<FormContainer {...defaultProps} />)

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Test Form')
    expect(screen.getByText('Form Content')).toBeInTheDocument()
  })

  it('renders form element', () => {
    const { container } = render(<FormContainer {...defaultProps} />)

    const form = container.querySelector('form')
    expect(form).toBeInTheDocument()
    expect(form).toHaveAttribute('noValidate')
  })

  it('calls onSubmit when form is submitted', () => {
    const { container } = render(<FormContainer {...defaultProps} />)
    const form = container.querySelector('form')

    fireEvent.submit(form!)
    expect(mockOnSubmit).toHaveBeenCalledTimes(1)
  })

  it('renders children inside form', () => {
    render(
      <FormContainer {...defaultProps}>
        <input type="text" placeholder="Test input" />
        <button type="submit">Submit</button>
      </FormContainer>
    )

    expect(screen.getByPlaceholderText('Test input')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument()
  })

  it('applies default className when containerClassName is not provided', () => {
    const { container } = render(<FormContainer {...defaultProps} />)

    const mainDiv = container.firstChild as HTMLElement
    expect(mainDiv).toHaveClass('text-text')
    expect(mainDiv).toHaveClass('flex')
    expect(mainDiv).toHaveClass('min-h-screen')
    expect(mainDiv).toHaveClass('w-full')
    expect(mainDiv).toHaveClass('flex-col')
    expect(mainDiv).toHaveClass('items-center')
    expect(mainDiv).toHaveClass('justify-normal')
    expect(mainDiv).toHaveClass('p-5')
  })

  it('applies custom containerClassName when provided', () => {
    const customClassName = 'custom-class bg-red-500'
    const { container } = render(
      <FormContainer {...defaultProps} containerClassName={customClassName} />
    )

    const mainDiv = container.firstChild as HTMLElement
    expect(mainDiv).toHaveClass('custom-class')
    expect(mainDiv).toHaveClass('bg-red-500')
    // Should still have default classes
    expect(mainDiv).toHaveClass('text-text')
    expect(mainDiv).toHaveClass('flex')
  })

  it('handles empty string containerClassName', () => {
    const { container } = render(<FormContainer {...defaultProps} containerClassName="" />)

    const mainDiv = container.firstChild as HTMLElement
    expect(mainDiv).toHaveClass('text-text')
    expect(mainDiv).toHaveClass('flex')
  })

  it('renders title with correct styling', () => {
    render(<FormContainer {...defaultProps} />)

    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toHaveClass('mb-2')
    expect(heading).toHaveClass('text-4xl')
    expect(heading).toHaveClass('font-bold')
    expect(heading).toHaveClass('text-gray-800')
    expect(heading).toHaveClass('dark:text-gray-200')
  })

  it('renders form container with correct styling', () => {
    const { container } = render(<FormContainer {...defaultProps} />)

    const formContainer = container.querySelector('.max-w-4xl')
    expect(formContainer).toBeInTheDocument()
    expect(formContainer).toHaveClass('w-full')
    expect(formContainer).toHaveClass('max-w-4xl')
    expect(formContainer).toHaveClass('overflow-hidden')
    expect(formContainer).toHaveClass('rounded-2xl')
    expect(formContainer).toHaveClass('bg-white')
    expect(formContainer).toHaveClass('shadow-2xl')
    expect(formContainer).toHaveClass('dark:bg-[#212529]')
  })

  it('prevents default form submission behavior', () => {
    const mockSubmit = jest.fn((e) => {
      e.preventDefault()
    })

    const { container } = render(<FormContainer {...defaultProps} onSubmit={mockSubmit} />)
    const form = container.querySelector('form')

    const submitEvent = new Event('submit', { bubbles: true, cancelable: true })
    form!.dispatchEvent(submitEvent)

    expect(mockSubmit).toHaveBeenCalled()
  })

  it('renders multiple children correctly', () => {
    render(
      <FormContainer {...defaultProps}>
        <div>Child 1</div>
        <div>Child 2</div>
        <div>Child 3</div>
      </FormContainer>
    )

    expect(screen.getByText('Child 1')).toBeInTheDocument()
    expect(screen.getByText('Child 2')).toBeInTheDocument()
    expect(screen.getByText('Child 3')).toBeInTheDocument()
  })
})
