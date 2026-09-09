import { renderHook, act, waitFor } from '@testing-library/react'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter, useSearchParams } from 'next/navigation'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

const mockFetchAlgoliaData = fetchAlgoliaData as jest.Mock
const mockUseRouter = useRouter as jest.Mock
const mockUseSearchParams = useSearchParams as jest.Mock

let mockSearchParams = new URLSearchParams()
let mockPush: jest.Mock

const useSearchPageOptions = {
  indexName: 'programs',
  pageTitle: 'OWASP Programs',
  defaultSortBy: 'default',
  defaultOrder: 'desc',
  hitsPerPage: 24,
}

const renderSearchPage = () =>
  renderHook(() => useSearchPage<{ key: string }>(useSearchPageOptions))

describe('useSearchPage', () => {
  beforeEach(() => {
    mockSearchParams = new URLSearchParams()
    mockPush = jest.fn()
    mockFetchAlgoliaData.mockResolvedValue({ hits: [], totalPages: 1 })
    mockUseRouter.mockImplementation(() => ({ push: mockPush }))
    mockUseSearchParams.mockImplementation(() => mockSearchParams)
    window.scrollTo = jest.fn()
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('resets to page 1 and fetches the replica index when sort changes on a later page', async () => {
    const { result } = renderSearchPage()
    await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(1))

    await act(async () => {
      result.current.handlePageChange(2)
    })
    await waitFor(() =>
      expect(mockFetchAlgoliaData).toHaveBeenLastCalledWith('programs', '', 2, 24, [])
    )

    await act(async () => {
      result.current.handleSortChange('name')
    })

    await waitFor(() =>
      expect(mockFetchAlgoliaData).toHaveBeenLastCalledWith('programs_name_desc', '', 1, 24, [])
    )
    expect(mockFetchAlgoliaData).not.toHaveBeenCalledWith('programs_name_desc', '', 2, 24, [])
    expect(result.current.sortBy).toBe('name')
    expect(result.current.currentPage).toBe(1)
  })

  it('adopts sort and order params from the URL when it changes', async () => {
    mockSearchParams = new URLSearchParams('sortBy=name&order=desc')

    const { result, rerender } = renderSearchPage()
    await waitFor(() => expect(result.current.sortBy).toBe('name'))
    expect(result.current.order).toBe('desc')
    await waitFor(() =>
      expect(mockFetchAlgoliaData).toHaveBeenLastCalledWith('programs_name_desc', '', 1, 24, [])
    )

    await act(async () => {
      mockSearchParams = new URLSearchParams()
      rerender()
    })

    await waitFor(() => expect(result.current.sortBy).toBe('default'))
    expect(result.current.order).toBe('desc')
    await waitFor(() =>
      expect(mockFetchAlgoliaData).toHaveBeenLastCalledWith('programs', '', 1, 24, [])
    )
  })

  it('ignores stale responses superseded by a newer request', async () => {
    let resolveInitial!: (value: { hits: { key: string }[]; totalPages: number }) => void
    let resolveNewer!: (value: { hits: { key: string }[]; totalPages: number }) => void
    const initial = new Promise<{ hits: { key: string }[]; totalPages: number }>((resolve) => {
      resolveInitial = resolve
    })
    const newer = new Promise<{ hits: { key: string }[]; totalPages: number }>((resolve) => {
      resolveNewer = resolve
    })

    mockFetchAlgoliaData.mockReturnValueOnce(initial).mockReturnValueOnce(newer)

    const { result } = renderSearchPage()
    await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(1))

    await act(async () => {
      result.current.handleSearch('owasp')
    })
    await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(2))

    await act(async () => {
      resolveNewer({ hits: [{ key: 'new' }], totalPages: 1 })
    })
    await waitFor(() => expect(result.current.items).toEqual([{ key: 'new' }]))

    await act(async () => {
      resolveInitial({ hits: [{ key: 'stale' }], totalPages: 1 })
    })
    await waitFor(() => expect(result.current.items).toEqual([{ key: 'new' }]))
  })
})
