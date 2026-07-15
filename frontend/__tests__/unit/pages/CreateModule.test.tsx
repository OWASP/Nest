import { useMutation, useQuery, useApolloClient } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter, useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import CreateModulePage from 'app/my/mentorship/programs/[programKey]/modules/create/page'

// Mock dependencies to isolate the component
jest.mock('@heroui/toast', () => ({ addToast: jest.fn() }))

jest.mock('@heroui/react', () => {
  const ReactActual = jest.requireActual('react')
  return {
    ...jest.requireActual('@heroui/react'),
    ComboBox: Object.assign(
      ({
        children,
        inputValue,
        onInputChange,
        onSelectionChange,
      }: {
        children?: React.ReactNode
        inputValue?: string
        onInputChange?: (value: string) => void
        onSelectionChange?: (key: React.Key | null) => void
      }) => {
        const childrenWithProps = ReactActual.Children.map(
          children,
          (child: React.ReactElement) => {
            if (!ReactActual.isValidElement(child)) return child
            return ReactActual.cloneElement(child as React.ReactElement<Record<string, unknown>>, {
              _onInputChange: onInputChange,
              _inputValue: inputValue,
              _onSelectionChange: onSelectionChange,
            })
          }
        )
        return <div data-testid="combobox">{childrenWithProps}</div>
      },
      {
        InputGroup: ({
          children,
          _onInputChange,
          _inputValue,
          _onSelectionChange,
        }: {
          children?: React.ReactNode
          _onInputChange?: (value: string) => void
          _inputValue?: string
          _onSelectionChange?: (key: React.Key | null) => void
        }) => {
          const childrenWithProps = ReactActual.Children.map(
            children,
            (child: React.ReactElement) => {
              if (!ReactActual.isValidElement(child)) return child
              return ReactActual.cloneElement(
                child as React.ReactElement<Record<string, unknown>>,
                { _onInputChange, _inputValue, _onSelectionChange }
              )
            }
          )
          return <div>{childrenWithProps}</div>
        },
        Popover: ({
          children,
          _onSelectionChange,
        }: {
          children?: React.ReactNode
          _onSelectionChange?: (key: React.Key | null) => void
        }) => {
          const childrenWithProps = ReactActual.Children.map(
            children,
            (child: React.ReactElement) => {
              if (!ReactActual.isValidElement(child)) return child
              return ReactActual.cloneElement(
                child as React.ReactElement<Record<string, unknown>>,
                { _onSelectionChange }
              )
            }
          )
          return <div>{childrenWithProps}</div>
        },
        Trigger: () => null,
      }
    ),
    Input: ({
      id,
      type,
      placeholder,
      className,
      onChange,
      value,
      onBlur,
      min,
      max,
      _onInputChange,
      _inputValue,
      _tfValue,
      _tfOnChange,
      _tfRequired,
      _tfInvalid,
    }: {
      id?: string
      type?: string
      placeholder?: string
      className?: string
      onChange?: React.ChangeEventHandler<HTMLInputElement>
      value?: string
      onBlur?: () => void
      min?: string | number
      max?: string | number
      _onInputChange?: (value: string) => void
      _inputValue?: string
      _tfValue?: string
      _tfOnChange?: (value: string) => void
      _tfRequired?: boolean
      _tfInvalid?: boolean
    }) => (
      <input
        id={id}
        type={type}
        placeholder={placeholder}
        className={className}
        min={min}
        max={max}
        onBlur={onBlur}
        value={
          _inputValue !== undefined ? _inputValue : _tfValue !== undefined ? _tfValue : value || ''
        }
        required={_tfRequired}
        aria-invalid={_tfInvalid}
        onChange={(e) => {
          onChange?.(e)
          _onInputChange?.(e.target.value)
          _tfOnChange?.(e.target.value)
        }}
      />
    ),
    Label: ({
      children,
      htmlFor,
      className,
    }: {
      children?: React.ReactNode
      htmlFor?: string
      className?: string
    }) => (
      <label htmlFor={htmlFor} className={className}>
        {children}
      </label>
    ),
    ListBox: Object.assign(
      ({
        children,
        _onSelectionChange,
      }: {
        children?: React.ReactNode
        _onSelectionChange?: (key: string) => void
      }) => {
        const childrenWithProps = ReactActual.Children.map(
          children,
          (child: React.ReactElement) => {
            if (!ReactActual.isValidElement(child)) return child
            return ReactActual.cloneElement(child as React.ReactElement<Record<string, unknown>>, {
              _onSelectionChange,
            })
          }
        )
        return <ul>{childrenWithProps}</ul>
      },
      {
        Item: ({
          children,
          id,
          textValue,
          _onSelectionChange,
          ...props
        }: {
          children?: React.ReactNode
          id?: string
          textValue?: string
          _onSelectionChange?: (key: string) => void
          [key: string]: unknown
        }) => (
          <li
            data-testid="listbox-item"
            data-id={id}
            data-key={id}
            role="option"
            aria-selected={false}
            aria-label={textValue}
            tabIndex={0}
            onClick={() => _onSelectionChange?.(id ?? '')}
            onKeyDown={(e) => e.key === 'Enter' && _onSelectionChange?.(id ?? '')}
            {...props}
          >
            {textValue ?? children}
          </li>
        ),
      }
    ),
    FieldError: ({ children }: { children?: React.ReactNode }) => (
      <span role="alert">{children}</span>
    ),
    TextField: ({
      children,
      value,
      onChange,
      isRequired,
      isInvalid,
    }: {
      children?: React.ReactNode
      value?: string
      onChange?: (value: string) => void
      isRequired?: boolean
      isInvalid?: boolean
    }) => (
      <div data-slot="textfield" data-invalid={isInvalid} data-required={isRequired}>
        {ReactActual.Children.map(children, (child: React.ReactElement) => {
          if (!ReactActual.isValidElement(child)) return child
          return ReactActual.cloneElement(child as React.ReactElement<Record<string, unknown>>, {
            _tfValue: value,
            _tfOnChange: onChange,
            _tfRequired: isRequired,
            _tfInvalid: isInvalid,
          })
        })}
      </div>
    ),
    Switch: Object.assign(
      ({
        children,
        isSelected,
        onChange,
        'aria-label': ariaLabel,
      }: {
        children?: React.ReactNode
        isSelected?: boolean
        onChange?: (value: boolean) => void
        'aria-label'?: string
      }) => (
        <div>
          <input
            type="checkbox"
            role="switch"
            aria-label={ariaLabel}
            checked={!!isSelected}
            onChange={(e) => onChange?.(e.target.checked)}
          />
          {children}
        </div>
      ),
      {
        Content: ({ children }: { children?: React.ReactNode }) => <div>{children}</div>,
        Control: ({ children }: { children?: React.ReactNode }) => <div>{children}</div>,
        Thumb: () => <span />,
      }
    ),
  }
})
// eslint-enable @typescript-eslint/no-explicit-any

jest.mock('@heroui/select', () => ({
  Select: ({
    children,
    onSelectionChange,
    label,
    id,
    isRequired,
    isInvalid,
    errorMessage,
    selectedKeys,
  }: any) => (
    <div>
      <label htmlFor={id}>{label}</label>
      <select
        id={id}
        aria-label={label}
        required={isRequired}
        aria-invalid={isInvalid}
        onChange={(e) => onSelectionChange?.(new Set([e.target.value]))}
      >
        <option value="">Select...</option>
        {(children as React.ReactElement[])?.map((child: any) => (
          <option key={child?.key ?? child?.props?.id} value={child?.props?.id ?? child?.key}>
            {child?.props?.children}
          </option>
        ))}
      </select>
      {isInvalid && errorMessage && <span>{errorMessage}</span>}
    </div>
  ),
  SelectItem: ({ children }: any) => null,
}))

jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
  ErrorDisplay: ({ title }: { title: string }) => <div>{title}</div>,
}))
jest.mock('next-auth/react', () => ({
  ...jest.requireActual('next-auth/react'),
  useSession: jest.fn(),
}))
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useParams: jest.fn(),
}))
jest.mock('@apollo/client/react', () => ({
  useMutation: jest.fn(),
  useQuery: jest.fn(),
  useApolloClient: jest.fn(),
}))

describe('CreateModulePage', () => {
  const mockPush = jest.fn()
  const mockReplace = jest.fn()
  const mockCreateModule = jest.fn()

  const mockQuery = jest.fn().mockResolvedValue({
    data: {
      searchProjects: [{ id: '123', name: 'Awesome Project' }],
    },
  })

  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush, replace: mockReplace })
    ;(useParams as jest.Mock).mockReturnValue({ programKey: 'test-program' })
    ;(useApolloClient as jest.Mock).mockReturnValue({
      query: mockQuery,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('submits the form and navigates to programs page', async () => {
    const user = userEvent.setup({ delay: null })

    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        managementProgram: {
          admins: [{ login: 'admin-user' }],
        },
      },
      loading: false,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([
      mockCreateModule.mockResolvedValue({
        data: {
          createModule: {
            key: 'my-test-module',
          },
        },
      }),
      { loading: false },
    ])

    render(<CreateModulePage />)

    // Fill all inputs
    await user.type(screen.getByLabelText('Name'), 'My Test Module')
    await user.type(screen.getByLabelText(/Description/i), 'This is a test module')
    await user.type(screen.getByLabelText(/Start Date/i), '2025-07-15')
    await user.type(screen.getByLabelText(/End Date/i), '2025-08-15')
    await user.selectOptions(
      screen.getByRole('combobox', { name: /Experience Level/i }),
      'BEGINNER'
    )
    await user.type(screen.getByLabelText(/Domains/i), 'AI, ML')
    await user.type(screen.getByLabelText(/Tags/i), 'react, graphql')

    const projectInput = await waitFor(() => {
      return screen.getByPlaceholderText('Start typing project name...')
    })

    await user.type(projectInput, 'Aw')

    await waitFor(
      () => {
        expect(mockQuery).toHaveBeenCalled()
      },
      { timeout: 1000 }
    )

    const projectOption = await waitFor(
      () => {
        return (
          screen.queryByRole('option', { name: /Awesome Project/i }) ||
          screen.queryByText('Awesome Project') ||
          document.querySelector('[data-key="123"]')
        )
      },
      { timeout: 2000 }
    )

    if (projectOption) {
      await user.click(projectOption)
    } else {
      await user.type(projectInput, '{ArrowDown}{Enter}')
    }

    await user.click(screen.getByRole('button', { name: /Create Module/i }))

    await waitFor(
      () => {
        expect(mockCreateModule).toHaveBeenCalled()
        expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/test-program')
      },
      { timeout: 10000 }
    )
  }, 15000)

  it('shows loading spinner while session or query is loading', () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'loading',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: undefined,
      loading: true,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<CreateModulePage />)
    expect(screen.getAllByAltText('Loading indicator')[0]).toBeInTheDocument()
  })

  it('shows access denied when query has an error', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'test-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: undefined,
      loading: false,
      error: new Error('Query failed'),
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<CreateModulePage />)

    await waitFor(() => {
      expect(screen.getByText('Access Denied')).toBeInTheDocument()
    })
  })

  it('shows access denied when user is unauthenticated', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'unauthenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { managementProgram: { admins: [] } },
      loading: false,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<CreateModulePage />)

    await waitFor(() => {
      expect(screen.getByText('Access Denied')).toBeInTheDocument()
    })
  })

  it('shows access denied when program data is not found', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'test-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { managementProgram: null },
      loading: false,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<CreateModulePage />)

    await waitFor(() => {
      expect(screen.getByText('Access Denied')).toBeInTheDocument()
    })
  })

  it('shows access denied and redirects when user is not an admin', async () => {
    jest.useFakeTimers()
    try {
      ;(useSession as jest.Mock).mockReturnValue({
        data: { user: { login: 'non-admin-user' } },
        status: 'authenticated',
      })
      ;(useQuery as unknown as jest.Mock).mockReturnValue({
        data: {
          managementProgram: {
            admins: [{ login: 'admin-user' }],
          },
        },
        loading: false,
      })
      ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

      render(<CreateModulePage />)

      await waitFor(() => {
        expect(screen.getByText('Access Denied')).toBeInTheDocument()
      })

      // Fast-forward past the redirect timeout
      jest.advanceTimersByTime(2000)

      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith('/my/mentorship')
      })
    } finally {
      jest.useRealTimers()
    }
  })

  it('renders form without error when program has start and end dates', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        managementProgram: {
          admins: [{ login: 'admin-user' }],
          startedAt: '2025-01-15T00:00:00Z',
          endedAt: '2025-12-31T00:00:00Z',
        },
      },
      loading: false,
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])

    render(<CreateModulePage />)

    await waitFor(() => {
      const moduleForm = screen.getByText('Create New Module')
      expect(moduleForm).toBeInTheDocument()
    })
  })
  it('handles form submission error by displaying inline error', async () => {
    const user = userEvent.setup({ delay: null })

    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        managementProgram: {
          admins: [{ login: 'admin-user' }],
          startedAt: '2025-01-15T00:00:00Z',
          endedAt: '2025-12-31T00:00:00Z',
        },
      },
      loading: false,
    })

    const mockCreateModuleError = jest.fn().mockRejectedValue(new Error('Network error'))
    ;(useMutation as unknown as jest.Mock).mockReturnValue([
      mockCreateModuleError,
      { loading: false },
    ])

    render(<CreateModulePage />)

    await user.type(screen.getByLabelText('Name'), 'Test Module')
    await user.type(screen.getByLabelText(/Description/i), 'Desc')
    await user.type(screen.getByLabelText(/Start Date/i), '2025-07-15')
    await user.type(screen.getByLabelText(/End Date/i), '2025-08-15')
    await user.selectOptions(
      screen.getByRole('combobox', { name: /Experience Level/i }),
      'BEGINNER'
    )

    const projectInput = await waitFor(() =>
      screen.getByPlaceholderText('Start typing project name...')
    )
    await user.type(projectInput, 'Aw')

    const projectOption = await waitFor(() => screen.getByText('Awesome Project'), {
      timeout: 2000,
    })
    await user.click(projectOption)

    await user.click(screen.getByRole('button', { name: /Create Module/i }))

    await waitFor(() => {
      expect(mockCreateModuleError).toHaveBeenCalled()
      // Error is displayed inline via validationErrors, not via addToast
      expect(addToast).not.toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Creation Failed' })
      )
    })
  })
  it('handles non-Error submission failure via handleAppError', async () => {
    const { handleAppError } = jest.requireMock('app/global-error')
    const user = userEvent.setup({ delay: null })

    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        managementProgram: {
          admins: [{ login: 'admin-user' }],
          startedAt: '2025-01-15T00:00:00Z',
          endedAt: '2025-12-31T00:00:00Z',
        },
      },
      loading: false,
    })

    const mockCreateModuleError = jest.fn().mockRejectedValue('String error')
    ;(useMutation as unknown as jest.Mock).mockReturnValue([
      mockCreateModuleError,
      { loading: false },
    ])

    render(<CreateModulePage />)

    await user.type(screen.getByLabelText('Name'), 'Test Module 2')
    await user.type(screen.getByLabelText(/Description/i), 'Desc 2')
    await user.type(screen.getByLabelText(/Start Date/i), '2025-07-15')
    await user.type(screen.getByLabelText(/End Date/i), '2025-08-15')
    await user.selectOptions(
      screen.getByRole('combobox', { name: /Experience Level/i }),
      'BEGINNER'
    )

    const projectInput = await waitFor(() =>
      screen.getByPlaceholderText('Start typing project name...')
    )
    await user.type(projectInput, 'Aw')
    const projectOption = await waitFor(() => screen.getByText('Awesome Project'), {
      timeout: 2000,
    })
    await user.click(projectOption)

    await user.click(screen.getByRole('button', { name: /Create Module/i }))

    await waitFor(() => {
      expect(mockCreateModuleError).toHaveBeenCalled()
      // Non-Error values fall through to handleAppError
      expect(handleAppError).toHaveBeenCalledWith('String error')
    })
  }, 10000)
})
