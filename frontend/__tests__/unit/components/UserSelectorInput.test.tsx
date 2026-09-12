import { act, fireEvent, render, screen } from '@testing-library/react'
import React from 'react'

import UserSelectorInput from 'components/UserSelectorInput'

const mockQuery = jest.fn()
const mockApolloClient = { query: mockQuery }

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useApolloClient: () => mockApolloClient,
}))

jest.mock('@heroui/react', () => ({
  Autocomplete: ({
    children,
    inputValue,
    onInputChange,
    onSelectionChange,
    onKeyDown,
    isInvalid,
    errorMessage,
    placeholder,
    isDisabled,
    description,
    id,
  }: {
    children?: React.ReactNode
    inputValue?: string
    onInputChange?: (v: string) => void
    onSelectionChange?: (key: unknown) => void
    onKeyDown?: React.KeyboardEventHandler<HTMLInputElement>
    isInvalid?: boolean
    errorMessage?: React.ReactNode
    placeholder?: string
    isDisabled?: boolean
    description?: React.ReactNode
    id?: string
  }) => (
    <div>
      <input
        id={id}
        data-testid="autocomplete-input"
        placeholder={placeholder}
        disabled={isDisabled}
        value={inputValue || ''}
        onChange={(e) => onInputChange?.(e.target.value)}
        onKeyDown={onKeyDown}
        data-invalid={isInvalid ? 'true' : 'false'}
      />
      {description && <span>{description}</span>}
      {errorMessage && <span>{errorMessage}</span>}
      <div>{children}</div>
      <button type="button" data-testid="select-login" onClick={() => onSelectionChange?.('alice')}>
        Login
      </button>
      <button type="button" data-testid="select-id" onClick={() => onSelectionChange?.('id-bob')}>
        ID
      </button>
      <button type="button" data-testid="select-raw" onClick={() => onSelectionChange?.('charlie')}>
        Raw
      </button>
      <button
        type="button"
        data-testid="select-num"
        onClick={() => onSelectionChange?.(123 as unknown as string)}
      >
        Num
      </button>
      <button type="button" data-testid="select-null" onClick={() => onSelectionChange?.(null)}>
        Null
      </button>
    </div>
  ),
  AutocompleteItem: ({ children }: { children?: React.ReactNode }) => <div>{children}</div>,
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({ src, alt }: { src: string; alt: string }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={src} alt={alt} />
  ),
}))

describe('UserSelectorInput', () => {
  const mockOnChange = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
    mockQuery.mockResolvedValue({
      data: {
        entityContributors: [
          { id: 'id-alice', login: 'alice', name: 'Alice', avatarUrl: 'https://example.com/a.png' },
          { id: 'id-bob', login: 'bob', name: '', avatarUrl: '' },
        ],
        searchUsers: [
          {
            id: 'id-search',
            login: 'searchuser',
            name: 'Search',
            avatarUrl: 'https://example.com/s.png',
          },
        ],
      },
    })
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('handles state, entity queries, error/disabled props, and pending unmount cleanups', async () => {
    render(
      <UserSelectorInput logins={[]} onChange={mockOnChange} disabled touched error="Required" />
    )
    expect(screen.getByPlaceholderText('Select a Project or Chapter first...')).toBeInTheDocument()
    const disabledInput = screen.getByTestId('autocomplete-input')
    expect(disabledInput).toBeDisabled()
    expect(disabledInput).toHaveAttribute('data-invalid', 'true')
    expect(screen.getByText('Required')).toBeInTheDocument()

    let resolveActive: (v: unknown) => void
    let rejectActive: (r?: unknown) => void
    mockQuery.mockReturnValueOnce(
      new Promise((r) => {
        resolveActive = r
      })
    )
    const { unmount: u1 } = render(
      <UserSelectorInput logins={[]} onChange={mockOnChange} projectKey="nest" />
    )
    u1()
    await act(async () => {
      resolveActive({ data: { entityContributors: [] } })
    })

    mockQuery.mockReturnValueOnce(
      new Promise((_, r) => {
        rejectActive = r
      })
    )
    const { unmount: u2 } = render(
      <UserSelectorInput logins={[]} onChange={mockOnChange} projectKey="nest" />
    )
    u2()
    await act(async () => {
      rejectActive(new Error('Fail'))
      await Promise.resolve()
    })

    let rerenderFn: (ui: React.ReactElement) => void
    await act(async () => {
      const res = render(
        <UserSelectorInput
          logins={[]}
          onChange={mockOnChange}
          projectKey="nest"
          touched={false}
          error="Err"
        />
      )
      rerenderFn = res.rerender
      await Promise.resolve()
    })
    expect(
      screen.getByPlaceholderText('Select a contributor or type username...')
    ).toBeInTheDocument()

    mockQuery.mockResolvedValueOnce({ data: { entityContributors: null } })
    await act(async () => {
      rerenderFn(<UserSelectorInput logins={[]} onChange={mockOnChange} chapterKey="london" />)
      await Promise.resolve()
    })

    mockQuery.mockRejectedValueOnce(new Error('Network error'))
    await act(async () => {
      rerenderFn(
        <UserSelectorInput
          logins={[]}
          onChange={mockOnChange}
          projectKey="nest"
          chapterKey="london"
        />
      )
      await Promise.resolve()
      await Promise.resolve()
    })
  })

  it('handles searching users, keyboard events, option selections, and duplicates', async () => {
    let rerenderFn: (ui: React.ReactElement) => void
    await act(async () => {
      const res = render(
        <UserSelectorInput logins={[]} onChange={mockOnChange} projectKey="nest" />
      )
      rerenderFn = res.rerender
      await Promise.resolve()
    })

    const input = screen.getByTestId('autocomplete-input')

    await act(async () => {
      fireEvent.change(input, { target: { value: 'sea' } })
      jest.advanceTimersByTime(350)
      await Promise.resolve()
      await Promise.resolve()
    })
    expect(screen.getByText('Search')).toBeInTheDocument()

    mockQuery.mockResolvedValueOnce({ data: { searchUsers: null } })
    await act(async () => {
      fireEvent.change(input, { target: { value: 'none' } })
      jest.advanceTimersByTime(350)
      await Promise.resolve()
      await Promise.resolve()
    })

    fireEvent.click(screen.getByTestId('select-login'))
    expect(mockOnChange).toHaveBeenCalledWith(['alice'])

    fireEvent.change(input, { target: { value: 'typing' } })
    expect(input).toHaveValue('')

    mockOnChange.mockClear()
    fireEvent.click(screen.getByTestId('select-id'))
    expect(mockOnChange).toHaveBeenCalledWith(['bob'])

    mockOnChange.mockClear()
    fireEvent.click(screen.getByTestId('select-raw'))
    expect(mockOnChange).toHaveBeenCalledWith(['charlie'])

    mockOnChange.mockClear()
    fireEvent.click(screen.getByTestId('select-num'))
    fireEvent.click(screen.getByTestId('select-null'))
    expect(mockOnChange).not.toHaveBeenCalled()

    fireEvent.keyDown(input, { key: 'a' })
    fireEvent.keyDown(input, { key: ',' })
    fireEvent.change(input, { target: { value: '  ' } })
    fireEvent.keyDown(input, { key: ' ' })
    fireEvent.change(input, { target: { value: '' } })
    fireEvent.keyDown(input, { key: 'Enter' })

    fireEvent.change(input, { target: { value: '@bob' } })
    fireEvent.keyDown(input, { key: ' ' })
    expect(mockOnChange).toHaveBeenCalledWith(['bob'])

    mockOnChange.mockClear()
    await act(async () => {
      rerenderFn(<UserSelectorInput logins={['alice']} onChange={mockOnChange} projectKey="nest" />)
      await Promise.resolve()
    })

    fireEvent.change(input, { target: { value: 'Alice' } })
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(mockOnChange).not.toHaveBeenCalled()

    input.setAttribute('aria-activedescendant', 'desc-id')
    fireEvent.change(input, { target: { value: 'charlie' } })
    fireEvent.keyDown(input, { key: 'Enter' })

    input.removeAttribute('aria-activedescendant')
    const activeOpt = document.createElement('div')
    activeOpt.setAttribute('role', 'option')
    activeOpt.setAttribute('data-focused', 'true')
    document.body.appendChild(activeOpt)
    fireEvent.keyDown(input, { key: 'Enter' })

    document.body.removeChild(activeOpt)
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(mockOnChange).toHaveBeenCalledWith(['alice', 'charlie'])
  })

  it('handles contributor list interactions and recipient badge removals', async () => {
    const { rerender } = render(
      <UserSelectorInput logins={['Alice', 'Bob']} onChange={mockOnChange} projectKey="nest" />
    )
    await act(async () => {
      await Promise.resolve()
    })

    fireEvent.click(screen.getByRole('button', { name: 'Remove recipient @Alice' }))
    expect(mockOnChange).toHaveBeenCalledWith(['Bob'])

    mockOnChange.mockClear()
    await act(async () => {
      rerender(<UserSelectorInput logins={[]} onChange={mockOnChange} projectKey="nest" />)
      await Promise.resolve()
    })

    fireEvent.click(screen.getByRole('button', { name: '+ Add All' }))
    expect(mockOnChange).toHaveBeenCalledWith(['alice', 'bob'])

    mockOnChange.mockClear()
    await act(async () => {
      rerender(
        <UserSelectorInput logins={['alice', 'bob']} onChange={mockOnChange} projectKey="nest" />
      )
      await Promise.resolve()
    })

    fireEvent.click(screen.getByRole('button', { name: '+ Add All' }))
    expect(mockOnChange).not.toHaveBeenCalled()

    mockOnChange.mockClear()
    await act(async () => {
      rerender(<UserSelectorInput logins={[]} onChange={mockOnChange} projectKey="nest" />)
      await Promise.resolve()
    })

    fireEvent.click(screen.getByRole('button', { name: 'alice @alice' }))
    expect(mockOnChange).toHaveBeenCalledWith(['alice'])
  })
})
