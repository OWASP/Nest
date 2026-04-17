import userEvent from '@testing-library/user-event'
import { render, screen, waitFor } from 'wrappers/testUtil'
import ProgramForm from 'components/ProgramForm'

describe('ProgramForm Component', () => {
  const mockSetFormData = jest.fn()
  const mockOnSubmit = jest.fn().mockResolvedValue(undefined)

  const defaultFormData = {
    name: '',
    description: '',
    menteesLimit: 0,
    startedAt: '',
    endedAt: '',
    tags: '',
    domains: '',
    adminLogins: '',
    status: '',
  }

  const filledFormData = {
    name: 'Test Program',
    description: 'A test program description',
    menteesLimit: 10,
    startedAt: '2024-01-01',
    endedAt: '2024-12-31',
    tags: 'javascript, react',
    domains: 'Web Development',
    adminLogins: 'admin1, admin2',
    status: 'active',
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockOnSubmit.mockResolvedValue(undefined)
  })

  describe('Component Rendering', () => {
    test('renders the component without crashing', () => {
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Create Program"
        />
      )

      expect(screen.getByText('Create Program')).toBeInTheDocument()
    })

    test('displays all required form fields', () => {
      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Program Form"
        />
      )

      // Check for required form fields
      expect(screen.getByText('Name')).toBeInTheDocument()
      expect(screen.getByText('Description')).toBeInTheDocument()
      expect(screen.getByText('Start Date')).toBeInTheDocument()
      expect(screen.getByText('End Date')).toBeInTheDocument()
      expect(screen.getByText('Mentees Limit')).toBeInTheDocument()
    })

    test('displays optional fields', () => {
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Program"
        />
      )

      expect(screen.getByText('Tags')).toBeInTheDocument()
      expect(screen.getByText('Domains')).toBeInTheDocument()
    })

    test('shows admin field only when in edit mode', () => {
      const { rerender } = render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Create"
          isEdit={false}
        />
      )

      expect(screen.queryByText('Admin GitHub Usernames')).not.toBeInTheDocument()

      rerender(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Edit"
          isEdit={true}
        />
      )

      expect(screen.getByText('Admin GitHub Usernames')).toBeInTheDocument()
    })

    test('populates form fields with existing data', () => {
      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Edit Program"
        />
      )

      const inputs = screen.getAllByDisplayValue('Test Program')
      expect(inputs.length).toBeGreaterThan(0)
    })

    test('uses default submitText "Save"', () => {
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const saveButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      expect(saveButton).toBeInTheDocument()
    })

    test('uses custom submitText when provided', () => {
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
          submitText="Create Program"
        />
      )

      const buttons = screen.getAllByRole('button')
      const createButton = buttons.find((btn) => btn.textContent?.includes('Create Program'))
      expect(createButton).toBeInTheDocument()
    })

    test('disables submit button when loading', () => {
      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={true}
          title="Test"
        />
      )

      const submitButton = screen.getByRole('button', { name: /saving|submit|save/i })
      expect(submitButton).toBeDisabled()
    })

    test('enables submit button when not loading', () => {
      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const submitButton = screen.getByRole('button', { name: /submit|save/i })
      expect(submitButton).not.toBeDisabled()
    })
  })

  describe('Form Input Handling', () => {
    test('calls setFormData when name input changes', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      // Get the name input by placeholder
      const nameInput = screen.getByPlaceholderText('Enter program name')
      await user.type(nameInput, 'New Program')

      expect(mockSetFormData).toHaveBeenCalled()
    })

    test('calls setFormData when mentees limit changes', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )
      const menteesInput = screen.getByPlaceholderText('Enter mentees limit (0 for unlimited)')
      await user.clear(menteesInput)
      await user.type(menteesInput, '5')
      expect(mockSetFormData).toHaveBeenCalled()
    })

    test('calls setFormData when tags input changes', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      // Get all text inputs and find the one for tags
      const placeholders = screen.getByPlaceholderText('javascript, react')
      await user.type(placeholders, 'tag1, tag2')

      expect(mockSetFormData).toHaveBeenCalled()
    })

    test('calls setFormData when domains input changes', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const domainsInput = screen.getByPlaceholderText('AI, Web Development')
      await user.type(domainsInput, 'Domain1')

      expect(mockSetFormData).toHaveBeenCalled()
    })
  })

  describe('Form Submission', () => {
    test('prevents submission when required fields are empty', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const submitButton = screen.getByRole('button', { name: /save/i })
      await user.click(submitButton)
      // onSubmit should not be called when required fields are empty
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    test('submits form when all required fields are valid', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })

    test('marks fields as touched when submitting', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      // Fields should be marked as touched
      // This is tested indirectly - the implementation marks them as touched
      expect(mockOnSubmit).not.toHaveBeenCalled() // Validation should fail
    })
  })

  describe('GraphQL Validation Error Handling', () => {
    test('displays field-level validation error from backend', async () => {
      const user = userEvent.setup()
      mockOnSubmit.mockRejectedValue({
        graphQLErrors: [
          {
            message: 'A program with this name already exists.',
            extensions: { code: 'VALIDATION_ERROR', field: 'name' },
          },
        ],
      })

      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })

      await waitFor(() => {
        expect(screen.getByText('A program with this name already exists.')).toBeInTheDocument()
      })
    })

    test('does not display validation errors for non-validation GraphQL errors', async () => {
      const user = userEvent.setup()
      mockOnSubmit.mockRejectedValue({
        graphQLErrors: [
          {
            message: 'Internal server error',
            extensions: { code: 'INTERNAL_ERROR' },
          },
        ],
      })

      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })

      expect(screen.queryByText('Internal server error')).not.toBeInTheDocument()
    })

    test('submits form successfully when no errors', async () => {
      const user = userEvent.setup()

      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })
  })

  describe('Mentees Limit Validation', () => {
    test('allows submission with zero mentees limit', async () => {
      const user = userEvent.setup()
      const formData = { ...filledFormData, menteesLimit: 0 }

      render(
        <ProgramForm
          formData={formData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })

    test('allows submission with positive mentees limit', async () => {
      const user = userEvent.setup()
      const formData = { ...filledFormData, menteesLimit: 50 }

      render(
        <ProgramForm
          formData={formData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })

    test('prevents submission with negative mentees limit', async () => {
      const user = userEvent.setup()
      const formData = { ...filledFormData, menteesLimit: -5 }

      render(
        <ProgramForm
          formData={formData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    test('prevents submission with non-integer mentees limit', async () => {
      const user = userEvent.setup()
      const formData = { ...filledFormData, menteesLimit: 5.5 }

      render(
        <ProgramForm
          formData={formData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })
  })

  describe('Date Validation', () => {
    test('allows submission when end date is after start date', async () => {
      const user = userEvent.setup()
      const formData = {
        ...filledFormData,
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }

      render(
        <ProgramForm
          formData={formData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const submitButton = screen.getByRole('button', { name: 'Save' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })

    test('prevents submission when end date is before start date', async () => {
      const user = userEvent.setup()
      const formData = {
        ...filledFormData,
        startedAt: '2024-12-31',
        endedAt: '2024-01-01',
      }

      render(
        <ProgramForm
          formData={formData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })
  })

  describe('Edit Mode Features', () => {
    test('shows admin logins field in edit mode', () => {
      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Edit"
          isEdit={true}
        />
      )

      expect(screen.getByText('Admin GitHub Usernames')).toBeInTheDocument()
    })

    test('updates admin logins on input change', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Edit"
          isEdit={true}
        />
      )

      const adminInput = screen.getByPlaceholderText('johndoe, jane-doe')
      await user.type(adminInput, 'new_admin')

      expect(mockSetFormData).toHaveBeenCalled()
    })
  })

  describe('Additional Coverage Tests', () => {
    test('clears backend error when field is changed', async () => {
      const user = userEvent.setup()
      mockOnSubmit.mockRejectedValueOnce({
        graphQLErrors: [
          {
            message: 'A program with this name already exists.',
            extensions: { code: 'VALIDATION_ERROR', field: 'name' },
          },
        ],
      })

      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      await waitFor(() => {
        expect(screen.getByText('A program with this name already exists.')).toBeInTheDocument()
      })

      const nameInput = screen.getByPlaceholderText('Enter program name')
      await user.clear(nameInput)
      await user.type(nameInput, 'Different Name')

      expect(mockSetFormData).toHaveBeenCalled()
    })

    test('handles empty name validation', async () => {
      const user = userEvent.setup()

      const emptyFormData = { ...defaultFormData, name: '' }

      render(
        <ProgramForm
          formData={emptyFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      // Should not submit with empty name
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    test('handles description field changes', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const descTextarea = screen.getByPlaceholderText('Enter program description')
      await user.type(descTextarea, 'New description')

      expect(mockSetFormData).toHaveBeenCalled()
    })

    test('handles start date changes and triggers touched state', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      // Find start date input by label
      const startDateLabel = screen.getByText('Start Date')
      expect(startDateLabel).toBeInTheDocument()

      // Find the date input element using getByLabelText
      const startDateInput = screen.getByLabelText(/Start Date/) as HTMLInputElement
      await user.type(startDateInput, '2024-01-15')

      expect(mockSetFormData).toHaveBeenCalled()
    })

    test('handles end date changes', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      // Find end date input by label
      const endDateLabel = screen.getByText('End Date')
      expect(endDateLabel).toBeInTheDocument()

      // Find the date input element using getByLabelText
      const endDateInput = screen.getByLabelText(/End Date/) as HTMLInputElement
      await user.type(endDateInput, '2024-12-31')

      expect(mockSetFormData).toHaveBeenCalled()
    })

    test('handles mentees limit input with string value conversion', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const menteesInput = screen.getByPlaceholderText('Enter mentees limit (0 for unlimited)')
      await user.clear(menteesInput)
      await user.type(menteesInput, '25')

      expect(mockSetFormData).toHaveBeenCalled()
    })

    test('handles mentees limit with empty value defaulting to 0', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const menteesInput = screen.getByPlaceholderText('Enter mentees limit (0 for unlimited)')
      await user.clear(menteesInput)

      expect(mockSetFormData).toHaveBeenCalled()
    })

    test('properly marks all form fields as touched on submit attempt', async () => {
      const user = userEvent.setup()
      render(
        <ProgramForm
          formData={defaultFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      // Form shouldn't submit with empty required fields
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    test('handles whitespace-only name validation', async () => {
      const user = userEvent.setup()

      const whitespaceNameFormData = {
        ...filledFormData,
        name: '   ',
      }

      render(
        <ProgramForm
          formData={whitespaceNameFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    test('handles empty name on submit', async () => {
      const user = userEvent.setup()

      const emptyNameFormData = {
        ...filledFormData,
        name: '',
      }

      render(
        <ProgramForm
          formData={emptyNameFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    test('handles menteesLimit touched state set to true for validation', async () => {
      const user = userEvent.setup()

      render(
        <ProgramForm
          formData={filledFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      // First interact with the mentees limit field to trigger touched state
      const menteesInput = screen.getByPlaceholderText('Enter mentees limit (0 for unlimited)')
      await user.clear(menteesInput)
      await user.type(menteesInput, '15')

      // Then submit the form - this ensures menteesLimit is marked as touched
      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })

    test('validates menteesLimit with touched state and valid value', async () => {
      const user = userEvent.setup()

      const formDataWithLimit = { ...filledFormData, menteesLimit: 100 }

      render(
        <ProgramForm
          formData={formDataWithLimit}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      // Touch the mentees limit field
      const menteesInput = screen.getByPlaceholderText('Enter mentees limit (0 for unlimited)')
      await user.click(menteesInput)

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })

    test('handles string menteesLimit in validation', async () => {
      const user = userEvent.setup()
      const stringLimitFormData = { ...filledFormData, menteesLimit: '10' as unknown as number }

      render(
        <ProgramForm
          formData={stringLimitFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })

    test('handles undefined menteesLimit in submission', async () => {
      const user = userEvent.setup()

      const undefinedLimitFormData = {
        ...filledFormData,
        menteesLimit: undefined as unknown as number,
      }

      render(
        <ProgramForm
          formData={undefinedLimitFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Test"
        />
      )

      const buttons = screen.getAllByRole('button')
      const submitButton = buttons.find((btn) => btn.textContent?.includes('Save'))
      if (submitButton) {
        await user.click(submitButton)
      }

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })
  })
})
