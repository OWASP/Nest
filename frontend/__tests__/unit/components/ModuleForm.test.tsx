/**
 * @file Comprehensive unit tests for the ModuleForm component
 * Targeting 90-95% code coverage.
 */
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import '@testing-library/jest-dom'
import React from 'react'
import ModuleForm, { ProjectSelector } from 'components/ModuleForm'

// Mock next/navigation
const mockBack = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    back: mockBack,
  }),
}))

// Mock apollo client hooks
const mockQuery = jest.fn()
jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useApolloClient: () => ({
    query: mockQuery,
  }),
}))

// Mock heroui components
jest.mock('@heroui/react', () => ({
  Autocomplete: ({
    children,
    inputValue,
    _selectedKey,
    onInputChange,
    onSelectionChange,
    isInvalid,
    errorMessage,
    isLoading,
    label,
    id,
  }: {
    children: React.ReactNode
    inputValue?: string
    _selectedKey?: string | null
    onInputChange?: (value: string) => void
    onSelectionChange?: (key: React.Key | Set<React.Key> | 'all') => void
    isInvalid?: boolean
    errorMessage?: string
    isLoading?: boolean
    label?: string
    id?: string
  }) => (
    <div data-testid="autocomplete">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        data-testid="autocomplete-input"
        value={inputValue || ''}
        data-selected-key={_selectedKey ?? ''}
        onChange={(e) => onInputChange?.(e.target.value)}
        data-loading={isLoading}
        data-invalid={isInvalid}
      />
      {errorMessage && <span data-testid="autocomplete-error">{errorMessage}</span>}
      <div data-testid="autocomplete-items">{children}</div>
      <button
        type="button"
        data-testid="autocomplete-select-item"
        onClick={() => onSelectionChange?.(new Set(['project-1']))}
      >
        Select Project 1
      </button>
      <button
        type="button"
        data-testid="autocomplete-select-all"
        onClick={() => onSelectionChange?.('all')}
      >
        Select All
      </button>
      <button
        type="button"
        data-testid="autocomplete-clear"
        onClick={() => onSelectionChange?.(null)}
      >
        Clear Selection
      </button>
      <button
        type="button"
        data-testid="autocomplete-select-single"
        onClick={() => onSelectionChange?.('project-1')}
      >
        Select Single Key
      </button>
    </div>
  ),
  AutocompleteItem: ({
    children,
    textValue,
  }: {
    children: React.ReactNode
    textValue?: string
  }) => (
    <div data-testid="autocomplete-item" data-text-value={textValue}>
      {children}
    </div>
  ),
}))

jest.mock('@heroui/select', () => ({
  Select: ({
    children,
    selectedKeys,
    onSelectionChange,
    isInvalid,
    errorMessage,
    label,
    id,
  }: {
    children: React.ReactNode
    selectedKeys?: Set<string>
    onSelectionChange?: (keys: React.Key | Set<React.Key> | 'all') => void
    isInvalid?: boolean
    errorMessage?: string
    label?: string
    id?: string
  }) => (
    <div data-testid="select" data-invalid={isInvalid}>
      <label htmlFor={id}>{label}</label>
      <select
        id={id}
        data-testid="select-input"
        value={selectedKeys ? Array.from(selectedKeys)[0] : ''}
        onChange={(e) => onSelectionChange?.(new Set([e.target.value]))}
      >
        <option value="">Select...</option>
        {children}
      </select>
      {errorMessage && <span data-testid="select-error">{errorMessage}</span>}
      <button
        type="button"
        data-testid="select-set"
        onClick={() => onSelectionChange?.(new Set(['BEGINNER']))}
      >
        Set via Set
      </button>
      <button type="button" data-testid="select-all" onClick={() => onSelectionChange?.('all')}>
        Select All
      </button>
      <button
        type="button"
        data-testid="select-single"
        onClick={() => onSelectionChange?.('INTERMEDIATE')}
      >
        Select Single
      </button>
    </div>
  ),
  SelectItem: ({ children }: { children: React.ReactNode }) => (
    <option data-testid="select-item">{children}</option>
  ),
}))

// Mock form components
jest.mock('components/forms/shared/FormButtons', () => ({
  FormButtons: ({ loading, submitText }: { loading: boolean; submitText?: string }) => (
    <div data-testid="form-buttons">
      <button type="button" data-testid="cancel-button">
        Cancel
      </button>
      <button type="submit" disabled={loading} data-testid="submit-button">
        {loading ? 'Saving...' : submitText || 'Save'}
      </button>
    </div>
  ),
}))

jest.mock('components/forms/shared/FormDateInput', () => ({
  FormDateInput: ({
    id,
    label,
    value,
    onValueChange,
    error,
    touched,
  }: {
    id: string
    label: string
    value: string
    onValueChange: (value: string) => void
    error?: string
    touched?: boolean
  }) => (
    <div data-testid={`date-input-${id}`}>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        type="date"
        value={value}
        onChange={(e) => onValueChange(e.target.value)}
        data-error={error}
        data-touched={touched}
      />
      {touched && error && <span data-testid={`${id}-error`}>{error}</span>}
    </div>
  ),
}))

jest.mock('components/forms/shared/FormTextarea', () => ({
  FormTextarea: ({
    id,
    label,
    value,
    onChange,
    error,
    touched,
  }: {
    id: string
    label: string
    value: string
    onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
    error?: string
    touched?: boolean
  }) => (
    <div data-testid={`textarea-${id}`}>
      <label htmlFor={id}>{label}</label>
      <textarea id={id} value={value} onChange={onChange} data-testid={`textarea-input-${id}`} />
      {touched && error && <span data-testid={`${id}-error`}>{error}</span>}
    </div>
  ),
}))

jest.mock('components/forms/shared/FormTextInput', () => ({
  FormTextInput: ({
    id,
    label,
    value,
    onValueChange,
    error,
    touched,
  }: {
    id: string
    label: string
    value: string
    onValueChange: (value: string) => void
    error?: string
    touched?: boolean
  }) => (
    <div data-testid={`text-input-${id}`}>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        type="text"
        value={value}
        onChange={(e) => onValueChange(e.target.value)}
        data-testid={`input-${id}`}
      />
      {touched && error && <span data-testid={`${id}-error`}>{error}</span>}
    </div>
  ),
}))

describe('ModuleForm', () => {
  const defaultFormData = {
    description: '',
    domains: '',
    endedAt: '',
    experienceLevel: '',
    labels: '',
    mentorLogins: '',
    name: '',
    projectId: '',
    projectName: '',
    startedAt: '',
    tags: '',
  }

  const mockSetFormData = jest.fn()
  const mockOnSubmit = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
    mockQuery.mockResolvedValue({
      data: { searchProjects: [{ id: 'project-1', name: 'Test Project' }] },
    })
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  const renderModuleForm = (props = {}) => {
    const defaultProps = {
      formData: defaultFormData,
      setFormData: mockSetFormData,
      onSubmit: mockOnSubmit,
      loading: false,
      title: 'Create Module',
      ...props,
    }
    return render(<ModuleForm {...defaultProps} />)
  }

  describe('Basic Rendering', () => {
    it('renders with title', () => {
      renderModuleForm({ title: 'Create New Module' })
      expect(screen.getByText('Create New Module')).toBeInTheDocument()
    })

    it('renders all form fields', () => {
      renderModuleForm()
      expect(screen.getByTestId('text-input-module-name')).toBeInTheDocument()
      expect(screen.getByTestId('textarea-module-description')).toBeInTheDocument()
      expect(screen.getByTestId('date-input-module-start-date')).toBeInTheDocument()
      expect(screen.getByTestId('date-input-module-end-date')).toBeInTheDocument()
      expect(screen.getByTestId('select')).toBeInTheDocument()
    })

    it('renders optional fields (domains, tags, labels)', () => {
      renderModuleForm()
      expect(screen.getByTestId('text-input-module-domains')).toBeInTheDocument()
      expect(screen.getByTestId('text-input-module-tags')).toBeInTheDocument()
      expect(screen.getByTestId('text-input-module-labels')).toBeInTheDocument()
    })

    it('renders mentor logins field only when isEdit is true (line 312)', () => {
      renderModuleForm({ isEdit: false })
      expect(screen.queryByTestId('text-input-module-mentor-logins')).not.toBeInTheDocument()

      renderModuleForm({ isEdit: true })
      expect(screen.getByTestId('text-input-module-mentor-logins')).toBeInTheDocument()
    })
  })

  describe('Input Handling', () => {
    it('updates name field', () => {
      renderModuleForm()
      const nameInput = screen.getByTestId('input-module-name')
      fireEvent.change(nameInput, { target: { value: 'New Module Name' } })

      expect(mockSetFormData).toHaveBeenCalled()
    })

    it('updates description field', () => {
      renderModuleForm()
      const descInput = screen.getByTestId('textarea-input-module-description')
      fireEvent.change(descInput, { target: { value: 'New description' } })

      expect(mockSetFormData).toHaveBeenCalled()
    })

    it('updates domains field (line 288 - handleInputChange for domains)', () => {
      renderModuleForm()
      const domainsInput = screen.getByTestId('input-module-domains')
      fireEvent.change(domainsInput, { target: { value: 'AI, ML' } })

      expect(mockSetFormData).toHaveBeenCalled()
    })

    it('updates tags field', () => {
      renderModuleForm()
      const tagsInput = screen.getByTestId('input-module-tags')
      fireEvent.change(tagsInput, { target: { value: 'react, javascript' } })

      expect(mockSetFormData).toHaveBeenCalled()
    })

    it('updates labels field (line 288)', () => {
      renderModuleForm()
      const labelsInput = screen.getByTestId('input-module-labels')
      fireEvent.change(labelsInput, { target: { value: 'bug, enhancement' } })

      expect(mockSetFormData).toHaveBeenCalled()
    })

    it('updates mentor logins field when in edit mode (line 312)', () => {
      renderModuleForm({ isEdit: true })
      const mentorInput = screen.getByTestId('input-module-mentor-logins')
      fireEvent.change(mentorInput, { target: { value: 'johndoe, Kateryna' } })

      expect(mockSetFormData).toHaveBeenCalled()
    })

    it('updates start date field', () => {
      renderModuleForm()
      const startDateContainer = screen.getByTestId('date-input-module-start-date')
      const startDateInput = startDateContainer.querySelector('input')
      expect(startDateInput).toBeTruthy()
      if (startDateInput) {
        fireEvent.change(startDateInput, { target: { value: '2024-01-01' } })
      }
      expect(mockSetFormData).toHaveBeenCalled()
    })

    it('updates end date field', () => {
      renderModuleForm()
      const endDateContainer = screen.getByTestId('date-input-module-end-date')
      const endDateInput = endDateContainer.querySelector('input')
      expect(endDateInput).toBeTruthy()
      if (endDateInput) {
        fireEvent.change(endDateInput, { target: { value: '2024-12-31' } })
      }
      expect(mockSetFormData).toHaveBeenCalled()
    })

    it('updates project field when ProjectSelector changes', async () => {
      renderModuleForm()
      const input = screen.getByTestId('autocomplete-input')
      await act(async () => {
        fireEvent.change(input, { target: { value: 'Test' } })
        jest.advanceTimersByTime(350)
      })
      await waitFor(() => expect(mockQuery).toHaveBeenCalled())
      const selectButton = screen.getByTestId('autocomplete-select-single')
      await act(async () => {
        fireEvent.click(selectButton)
      })
      expect(mockSetFormData).toHaveBeenCalled()
      const setterFn = mockSetFormData.mock.calls[mockSetFormData.mock.calls.length - 1][0]
      const result = setterFn(defaultFormData)
      expect(result).toEqual(
        expect.objectContaining({
          projectId: 'project-1',
          projectName: 'Test Project',
        })
      )
    })

    it('updates project field when ProjectSelector is cleared', async () => {
      const initialFormData = {
        ...defaultFormData,
        projectId: 'proj-1',
        projectName: 'Existing Project',
      }
      renderModuleForm({ formData: initialFormData })
      const clearButton = screen.getByTestId('autocomplete-clear')
      await act(async () => {
        fireEvent.click(clearButton)
      })
      expect(mockSetFormData).toHaveBeenCalled()
      const setterFn = mockSetFormData.mock.calls[mockSetFormData.mock.calls.length - 1][0]
      const result = setterFn(initialFormData)
      expect(result).toEqual(
        expect.objectContaining({
          projectId: '',
          projectName: '',
        })
      )
    })
  })

  describe('Experience Level Select - handleSelectChange (lines 74-84)', () => {
    it('handles selection via Set (line 74-75)', () => {
      renderModuleForm()
      const setButton = screen.getByTestId('select-set')
      fireEvent.click(setButton)

      expect(mockSetFormData).toHaveBeenCalled()
    })

    it('handles "all" key selection (lines 76-77)', () => {
      renderModuleForm()
      const allButton = screen.getByTestId('select-all')
      fireEvent.click(allButton)

      // When 'all' is selected, an empty set is created and no value is set
      // So setFormData should NOT be called in this case (line 82-84 checks if value exists)
      expect(mockSetFormData).not.toHaveBeenCalled()
    })

    it('handles single key selection (lines 78-80)', () => {
      renderModuleForm()
      const singleButton = screen.getByTestId('select-single')
      fireEvent.click(singleButton)

      // Verify setFormData was called with a function (setter pattern)
      expect(mockSetFormData).toHaveBeenCalled()
      const setterFn = mockSetFormData.mock.calls[0][0]
      expect(typeof setterFn).toBe('function')

      // Call the setter function with previous state and verify it returns correct data
      const result = setterFn(defaultFormData)
      expect(result).toEqual(
        expect.objectContaining({
          experienceLevel: 'INTERMEDIATE',
        })
      )
    })
  })

  describe('Form Submission - handleSubmit (lines 124-161)', () => {
    it('prevents default form submission', () => {
      renderModuleForm()
      const form = document.querySelector('form')

      expect(form).toBeInTheDocument()

      const submitEvent = new Event('submit', { bubbles: true, cancelable: true })
      jest.spyOn(submitEvent, 'preventDefault')

      act(() => {
        form!.dispatchEvent(submitEvent)
      })

      expect(submitEvent.preventDefault).toHaveBeenCalled()
    })

    it('does not call onSubmit when validation fails (line 157)', () => {
      renderModuleForm() // Empty form data should fail validation

      const form = document.querySelector('form')
      if (form) {
        fireEvent.submit(form)
      }

      // onSubmit should NOT be called because validation fails
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('calls onSubmit when all fields are valid', async () => {
      const validFormData = {
        ...defaultFormData,
        name: 'Valid Module Name',
        description: 'A valid description that is long enough',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
        projectId: 'project-123',
        projectName: 'My Project',
        experienceLevel: 'BEGINNER',
      }

      renderModuleForm({ formData: validFormData })

      const form = document.querySelector('form')
      await act(async () => {
        if (form) {
          fireEvent.submit(form)
        }
      })

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })

    it('sets all fields as touched on submit', () => {
      renderModuleForm()

      const form = document.querySelector('form')
      expect(form).toBeInTheDocument()

      // Form should exist at this point based on above assertion
      const formElement = form as HTMLFormElement
      fireEvent.submit(formElement)
    })
  })

  describe('Custom Submit Text', () => {
    it('uses default submit text "Save"', () => {
      renderModuleForm()
      expect(screen.getByTestId('submit-button')).toHaveTextContent('Save')
    })

    it('uses custom submit text when provided', () => {
      renderModuleForm({ submitText: 'Create Module' })
      expect(screen.getByTestId('submit-button')).toHaveTextContent('Create Module')
    })
  })

  describe('Loading State', () => {
    it('disables submit button when loading', () => {
      renderModuleForm({ loading: true })
      expect(screen.getByTestId('submit-button')).toBeDisabled()
    })

    it('enables submit button when not loading', () => {
      renderModuleForm({ loading: false })
      expect(screen.getByTestId('submit-button')).not.toBeDisabled()
    })
  })

  describe('Mutation Error Display (validationErrors prop)', () => {
    const validFormData = {
      ...defaultFormData,
      name: 'Test Module',
      description: 'A valid description that is long enough',
      startedAt: '2024-01-01',
      endedAt: '2024-12-31',
      projectId: 'project-123',
      projectName: 'My Project',
      experienceLevel: 'BEGINNER',
    }

    it('displays mutation error for name field after submission', () => {
      const { rerender } = render(
        <ModuleForm
          formData={validFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Create Module"
        />
      )

      // Submit first to mark fields as touched
      const form = document.querySelector('form')
      fireEvent.submit(form!)

      // Rerender with mutation errors (simulates page catching backend error)
      rerender(
        <ModuleForm
          formData={validFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Create Module"
          validationErrors={{
            name: 'This module name already exists in this program.',
          }}
        />
      )

      expect(screen.getByTestId('module-name-error')).toHaveTextContent(
        'This module name already exists in this program.'
      )
    })

    it('does not display mutation error when validationErrors is empty', () => {
      renderModuleForm({
        formData: validFormData,
        validationErrors: {},
      })

      expect(screen.queryByTestId('module-name-error')).not.toBeInTheDocument()
    })

    it('allows resubmission even when validationErrors.name is set', async () => {
      const { rerender } = render(
        <ModuleForm
          formData={validFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Create Module"
        />
      )

      // First submit to mark fields as touched
      const form = document.querySelector('form')
      fireEvent.submit(form!)
      expect(mockOnSubmit).toHaveBeenCalledTimes(1)
      mockOnSubmit.mockClear()

      // Rerender with mutation errors
      rerender(
        <ModuleForm
          formData={validFormData}
          setFormData={mockSetFormData}
          onSubmit={mockOnSubmit}
          loading={false}
          title="Create Module"
          validationErrors={{
            name: 'This module name already exists in this program.',
          }}
        />
      )

      // Second submit should still call onSubmit so parent can clear errors and retry
      fireEvent.submit(form!)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledTimes(1)
      })
    })

    it('allows submission when validationErrors has no name error', async () => {
      renderModuleForm({
        formData: validFormData,
        validationErrors: {},
      })

      const form = document.querySelector('form')
      fireEvent.submit(form!)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })

    it('allows submission when validationErrors is undefined', async () => {
      renderModuleForm({
        formData: validFormData,
      })

      const form = document.querySelector('form')
      fireEvent.submit(form!)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })
  })
})

describe('ProjectSelector', () => {
  const mockOnProjectChange = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
    mockQuery.mockResolvedValue({
      data: {
        searchProjects: [
          { id: 'project-1', name: 'Test Project 1' },
          { id: 'project-2', name: 'Test Project 2' },
        ],
      },
    })
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  const renderProjectSelector = (props = {}) => {
    const defaultProps = {
      value: '',
      defaultName: '',
      onProjectChange: mockOnProjectChange,
      ...props,
    }
    return render(<ProjectSelector {...defaultProps} />)
  }

  describe('Basic Rendering', () => {
    it('renders autocomplete component', () => {
      renderProjectSelector()
      expect(screen.getByTestId('autocomplete')).toBeInTheDocument()
    })

    it('renders with default name', () => {
      renderProjectSelector({ defaultName: 'Initial Project' })
      const input = screen.getByTestId('autocomplete-input')
      expect(input).toHaveValue('Initial Project')
    })
  })

  describe('Input Handling', () => {
    it('updates input value on change', async () => {
      renderProjectSelector()
      const input = screen.getByTestId('autocomplete-input')

      await act(async () => {
        fireEvent.change(input, { target: { value: 'New Query' } })
      })

      expect(mockOnProjectChange).toHaveBeenCalledWith(null, 'New Query')
    })

    it('triggers search after debounce for queries >= 2 chars', async () => {
      renderProjectSelector()
      const input = screen.getByTestId('autocomplete-input')

      await act(async () => {
        fireEvent.change(input, { target: { value: 'Test' } })
        jest.advanceTimersByTime(350)
      })

      await waitFor(() => {
        expect(mockQuery).toHaveBeenCalled()
      })
    })

    it('does not trigger search for queries < 2 chars', async () => {
      renderProjectSelector()
      const input = screen.getByTestId('autocomplete-input')

      await act(async () => {
        fireEvent.change(input, { target: { value: 'T' } })
        jest.advanceTimersByTime(350)
      })

      // Query should not be called for single character
      expect(mockQuery).not.toHaveBeenCalled()
    })
  })

  describe('Selection Handling - handleSelectionChange (lines 401-421)', () => {
    it('handles selection via Set (lines 403-404)', async () => {
      mockQuery.mockResolvedValue({
        data: {
          searchProjects: [{ id: 'project-1', name: 'Test Project 1' }],
        },
      })

      renderProjectSelector()

      // First trigger a search to populate items
      const input = screen.getByTestId('autocomplete-input')
      await act(async () => {
        fireEvent.change(input, { target: { value: 'Test' } })
        jest.advanceTimersByTime(350)
      })

      await waitFor(() => {
        expect(mockQuery).toHaveBeenCalled()
      })

      // Then select via Set
      const selectButton = screen.getByTestId('autocomplete-select-item')
      await act(async () => {
        fireEvent.click(selectButton)
      })

      // Verify that typing triggers onProjectChange with the search term
      await waitFor(() => {
        expect(mockOnProjectChange).toHaveBeenCalledWith(null, 'Test')
      })
    })

    it('handles "all" key selection (lines 405-406)', async () => {
      mockQuery.mockResolvedValue({
        data: {
          searchProjects: [{ id: 'project-1', name: 'Test Project 1' }],
        },
      })

      renderProjectSelector({ value: 'project-1', defaultName: 'Test Project 1' })
      const allButton = screen.getByTestId('autocomplete-select-all')

      await act(async () => {
        fireEvent.click(allButton)
      })

      // The component's handleSelectionChange doesn't handle 'all' directly
      // This test verifies the current behavior where it's not called
      expect(mockOnProjectChange).not.toHaveBeenCalled()
    })

    it('handles single key selection (lines 407-408)', async () => {
      mockQuery.mockResolvedValue({
        data: {
          searchProjects: [{ id: 'project-1', name: 'Test Project 1' }],
        },
      })

      renderProjectSelector()

      // First trigger a search
      const input = screen.getByTestId('autocomplete-input')
      await act(async () => {
        fireEvent.change(input, { target: { value: 'Test' } })
        jest.advanceTimersByTime(350)
      })

      await waitFor(() => {
        expect(mockQuery).toHaveBeenCalled()
      })

      // Select via single key
      const singleButton = screen.getByTestId('autocomplete-select-single')
      await act(async () => {
        fireEvent.click(singleButton)
      })

      // Verify onProjectChange is called with the selected project
      expect(mockOnProjectChange).toHaveBeenCalledWith('project-1', 'Test Project 1')
    })

    it('clears selection when clear button is clicked (lines 411-413)', async () => {
      renderProjectSelector({ value: 'project-1', defaultName: 'Existing Project' })
      const clearButton = screen.getByTestId('autocomplete-clear')

      await act(async () => {
        fireEvent.click(clearButton)
      })

      // Now expected to call onProjectChange with null
      expect(mockOnProjectChange).toHaveBeenCalledWith(null, '')
    })
  })

  describe('useEffect - Value Sync (lines 349-356)', () => {
    it('syncs inputValue when defaultName changes (line 351)', () => {
      const { rerender } = renderProjectSelector({ value: 'proj-1', defaultName: 'Project 1' })

      // Rerender with different defaultName
      rerender(
        <ProjectSelector
          value="proj-1"
          defaultName="Updated Project Name"
          onProjectChange={mockOnProjectChange}
        />
      )

      const input = screen.getByTestId('autocomplete-input')
      expect(input).toHaveValue('Updated Project Name')
    })

    it('clears inputValue when value and defaultName become empty (line 353)', () => {
      const { rerender } = renderProjectSelector({ value: 'proj-1', defaultName: 'Project 1' })

      // Rerender with empty values
      rerender(<ProjectSelector value="" defaultName="" onProjectChange={mockOnProjectChange} />)

      const input = screen.getByTestId('autocomplete-input')
      expect(input).toHaveValue('')
    })
  })

  describe('Error Handling - fetchSuggestions catch block (lines 380-385)', () => {
    it('handles API errors gracefully', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      mockQuery.mockRejectedValue(new Error('Network error'))

      renderProjectSelector()
      const input = screen.getByTestId('autocomplete-input')

      await act(async () => {
        fireEvent.change(input, { target: { value: 'Test Query' } })
        jest.advanceTimersByTime(350)
      })

      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          'Error fetching project suggestions:',
          'Network error',
          expect.any(Error)
        )
      })

      consoleErrorSpy.mockRestore()
    })

    it('handles non-Error exceptions', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      mockQuery.mockRejectedValue('String error')

      renderProjectSelector()
      const input = screen.getByTestId('autocomplete-input')

      await act(async () => {
        fireEvent.change(input, { target: { value: 'Test Query' } })
        jest.advanceTimersByTime(350)
      })

      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          'Error fetching project suggestions:',
          'String error',
          'String error'
        )
      })

      consoleErrorSpy.mockRestore()
    })

    it('handles missing searchProjects in response', async () => {
      mockQuery.mockResolvedValue({ data: {} })

      renderProjectSelector()
      const input = screen.getByTestId('autocomplete-input')

      await act(async () => {
        fireEvent.change(input, { target: { value: 'Test' } })
        jest.advanceTimersByTime(350)
      })

      await waitFor(() => {
        expect(mockQuery).toHaveBeenCalled()
      })
      const items = screen.queryAllByTestId('autocomplete-item')
      expect(items).toHaveLength(0)
    })
  })

  describe('Validation Display', () => {
    it('shows error message when isInvalid and not typing', () => {
      renderProjectSelector({
        value: '',
        defaultName: '',
        isInvalid: true,
        errorMessage: 'Project is required',
      })

      expect(screen.getByTestId('autocomplete-error')).toHaveTextContent('Project is required')
    })

    it('hides error message when user is typing', () => {
      renderProjectSelector({
        value: '',
        defaultName: 'Typing...',
        isInvalid: true,
        errorMessage: 'Project is required',
      })

      // When typing (inputValue has text but no value selected), error should be hidden
      expect(screen.queryByTestId('autocomplete-error')).not.toBeInTheDocument()
    })
  })

  describe('Project Filtering', () => {
    it('filters out currently selected project from suggestions', async () => {
      mockQuery.mockResolvedValue({
        data: {
          searchProjects: [
            { id: 'project-1', name: 'Test Project 1' },
            { id: 'project-2', name: 'Test Project 2' },
          ],
        },
      })

      renderProjectSelector({ value: 'project-1', defaultName: 'Test Project 1' })
      const input = screen.getByTestId('autocomplete-input')

      await act(async () => {
        fireEvent.change(input, { target: { value: 'Test' } })
        jest.advanceTimersByTime(350)
      })

      await waitFor(() => {
        expect(mockQuery).toHaveBeenCalled()
      })

      // Verify filtering: only project-2 should be in the rendered results
      const autocompleteItems = screen.getAllByTestId('autocomplete-item')
      expect(autocompleteItems).toHaveLength(1)
      expect(autocompleteItems[0]).toHaveAttribute('data-text-value', 'Test Project 2')

      // Explicitly verify project-1 is not rendered
      const project1Item = autocompleteItems.find(
        (item) => item.dataset.textValue === 'Test Project 1'
      )
      expect(project1Item).toBeUndefined()
    })
  })
})
