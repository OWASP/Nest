import '@testing-library/jest-dom'
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import { SearchChapterNamesDocument } from 'types/__generated__/chapterQueries.generated'
import { SearchProjectNamesDocument } from 'types/__generated__/projectQueries.generated'

import EntitySelectorInput from 'components/EntitySelectorInput'

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
    isInvalid,
    errorMessage,
    label,
    id,
    placeholder,
  }: {
    children?: React.ReactNode
    inputValue?: string
    onInputChange?: (value: string) => void
    onSelectionChange?: (key: React.Key | null) => void
    isInvalid?: boolean
    errorMessage?: string
    label?: string
    id?: string
    placeholder?: string
  }) => (
    <div data-testid="autocomplete">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        data-testid="autocomplete-input"
        placeholder={placeholder}
        value={inputValue || ''}
        onChange={(e) => onInputChange?.(e.target.value)}
        data-invalid={isInvalid ? 'true' : 'false'}
      />
      {errorMessage && <span data-testid="autocomplete-error">{errorMessage}</span>}
      <div>{children}</div>
      <button
        type="button"
        data-testid="select-item"
        onClick={() => {
          onSelectionChange?.('www-project-nest')
          onInputChange?.('OWASP Nest')
        }}
      >
        Select Item
      </button>
      <button
        type="button"
        data-testid="select-item-by-id"
        onClick={() => {
          onSelectionChange?.('item-id-123')
          onInputChange?.('Custom Project')
        }}
      >
        Select Item By ID
      </button>
      <button
        type="button"
        data-testid="select-unmatched-key"
        onClick={() => onSelectionChange?.('unmatched-key-999')}
      >
        Select Unmatched Key
      </button>
      <button type="button" data-testid="clear-selection" onClick={() => onSelectionChange?.(null)}>
        Clear Selection
      </button>
    </div>
  ),
  AutocompleteItem: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="autocomplete-item">{children}</div>
  ),
}))

describe('EntitySelectorInput', () => {
  const mockOnChange = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
    mockQuery.mockResolvedValue({
      data: {
        searchProjects: [
          { id: 'proj-1', key: 'www-project-nest', name: 'OWASP Nest' },
          { id: 'item-id-123', key: '', name: 'Custom Project' },
        ],
      },
    })
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('renders project/chapter layouts and error states correctly', () => {
    const { rerender } = render(
      <EntitySelectorInput
        value=""
        onChange={mockOnChange}
        entityType="project"
        error="Error message"
      />
    )

    expect(screen.getByLabelText('Project Name')).toHaveAttribute('id', 'projectKey')
    expect(screen.getByPlaceholderText('Start typing project name...')).toBeInTheDocument()
    expect(screen.getByTestId('autocomplete-error')).toHaveTextContent('Error message')

    rerender(<EntitySelectorInput value="" onChange={mockOnChange} entityType="chapter" />)

    expect(screen.getByLabelText('Chapter Name')).toHaveAttribute('id', 'chapterKey')
    expect(screen.getByPlaceholderText('Start typing chapter name...')).toBeInTheDocument()
  })

  it('queries GraphQL endpoint for project and chapter types and handles null responses', async () => {
    const { rerender } = render(
      <EntitySelectorInput value="" onChange={mockOnChange} entityType="project" />
    )

    const input = screen.getByTestId('autocomplete-input')
    await act(async () => {
      fireEvent.change(input, { target: { value: 'nest' } })
      jest.advanceTimersByTime(350)
    })

    await waitFor(() => {
      expect(mockQuery).toHaveBeenCalledWith({
        query: SearchProjectNamesDocument,
        variables: { query: 'nest' },
        fetchPolicy: 'network-only',
      })
    })
    expect(screen.getByText('OWASP Nest')).toBeInTheDocument()

    mockQuery.mockResolvedValueOnce({ data: { searchProjects: null } })
    await act(async () => {
      fireEvent.change(input, { target: { value: 'none' } })
      jest.advanceTimersByTime(350)
    })
    await waitFor(() => expect(mockQuery).toHaveBeenCalled())

    mockQuery.mockResolvedValueOnce({ data: { searchChapters: null } })
    rerender(<EntitySelectorInput value="" onChange={mockOnChange} entityType="chapter" />)

    await act(async () => {
      fireEvent.change(input, { target: { value: 'lond' } })
      jest.advanceTimersByTime(350)
    })

    await waitFor(() => {
      expect(mockQuery).toHaveBeenCalledWith({
        query: SearchChapterNamesDocument,
        variables: { query: 'lond' },
        fetchPolicy: 'network-only',
      })
    })
    expect(screen.queryByTestId('autocomplete-item')).not.toBeInTheDocument()
  })

  it('matches typed input with suggestions and clears selection when erased', async () => {
    const { rerender } = render(
      <EntitySelectorInput value="" onChange={mockOnChange} entityType="project" />
    )

    const input = screen.getByTestId('autocomplete-input')
    await act(async () => {
      fireEvent.change(input, { target: { value: 'owasp nest' } })
      jest.advanceTimersByTime(350)
    })

    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalledWith('nest')
    })

    rerender(<EntitySelectorInput value="" onChange={mockOnChange} entityType="chapter" />)
    mockQuery.mockResolvedValueOnce({
      data: { searchChapters: [{ id: 'chap-1', key: 'www-chapter-london', name: 'OWASP London' }] },
    })

    await act(async () => {
      fireEvent.change(input, { target: { value: 'owasp london' } })
      jest.advanceTimersByTime(350)
    })

    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalledWith('london')
    })

    mockOnChange.mockClear()

    await act(async () => {
      fireEvent.change(input, { target: { value: '' } })
    })

    expect(mockOnChange).toHaveBeenCalledWith('')
  })

  it('handles dropdown selections by key, by item.id, unmatched keys, and null clearing', async () => {
    render(<EntitySelectorInput value="" onChange={mockOnChange} entityType="project" />)

    const input = screen.getByTestId('autocomplete-input')
    await act(async () => {
      fireEvent.change(input, { target: { value: 'nest' } })
      jest.advanceTimersByTime(350)
    })

    await act(async () => {
      fireEvent.click(screen.getByTestId('select-item'))
    })
    expect(mockOnChange).toHaveBeenCalledWith('nest')
    expect(input).toHaveValue('OWASP Nest')

    await act(async () => {
      fireEvent.click(screen.getByTestId('select-item-by-id'))
    })
    expect(input).toHaveValue('Custom Project')

    mockOnChange.mockClear()
    await act(async () => {
      fireEvent.click(screen.getByTestId('select-unmatched-key'))
    })
    expect(mockOnChange).not.toHaveBeenCalled()

    await act(async () => {
      fireEvent.click(screen.getByTestId('clear-selection'))
    })
    expect(mockOnChange).toHaveBeenCalledWith('')
  })

  it('resets internal input state when value prop becomes empty', async () => {
    const { rerender } = render(
      <EntitySelectorInput value="nest" onChange={mockOnChange} entityType="project" />
    )

    const input = screen.getByTestId('autocomplete-input')
    await act(async () => {
      fireEvent.change(input, { target: { value: 'nest' } })
      jest.advanceTimersByTime(350)
    })

    await act(async () => {
      fireEvent.click(screen.getByTestId('select-item'))
    })

    expect(input).toHaveValue('OWASP Nest')

    rerender(<EntitySelectorInput value="" onChange={mockOnChange} entityType="project" />)

    expect(screen.getByTestId('autocomplete-input')).toHaveValue('')
  })
})
