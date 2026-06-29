import { useQuery, useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import mockProgramDetailsData from '@mockData/mockProgramData'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { useSession } from 'next-auth/react'
import React from 'react'
import { render } from 'wrappers/testUtil'
import { handleAppError } from 'app/global-error'
import ProgramDetailsPage from 'app/my/mentorship/programs/[programKey]/page'
import '@testing-library/jest-dom'
import { ProgramStatusEnum } from 'types/__generated__/graphql'

let capturedSetStatus: ((status: string) => void) | null = null

jest.mock('components/cards/Header', () => {
  return function MockHeader(props: {
    title: string
    canUpdateStatus?: boolean
    setStatus?: (status: string) => void
  }) {
    capturedSetStatus = props.setStatus || null
    return (
      <div data-testid="details-card">
        <h1>{props.title}</h1>
        {props.canUpdateStatus && (
          <div>
            <button aria-label="Program actions menu">Program actions menu</button>
            <button role="menuitem" onClick={() => props.setStatus?.('PUBLISHED')}>
              Publish
            </button>
          </div>
        )}
      </div>
    )
  }
})

jest.mock('components/cards/Summary', () => {
  return function MockSummary(props: { summary: string }) {
    return <p>{props.summary}</p>
  }
})

jest.mock('components/cards/Metadata', () => {
  return function MockMetadata(props: { details?: Array<{ label: string; value: string }> }) {
    return (
      <div data-testid="details-content">
        {props.details?.map((detail: { label: string; value: string }) => (
          <div key={detail.label}>
            <span>{detail.label}</span>
            <span>{detail.value}</span>
          </div>
        ))}
      </div>
    )
  }
})

jest.mock('components/cards/PageWrapper', () => {
  return function MockWrapper({ children }: { children: React.ReactNode }) {
    return <div>{children}</div>
  }
})

jest.mock('components/cards/RepositoriesModules', () => {
  return function MockReposModules() {
    return <div />
  }
})

jest.mock('components/cards/Tags', () => {
  return function MockTags() {
    return <div />
  }
})

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
  useMutation: jest.fn(() => [jest.fn()]),
}))

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: () => ({ replace: jest.fn() }),
  useParams: () => ({ programKey: 'test-program' }),
  useSearchParams: () => new URLSearchParams(),
}))

jest.mock('next-auth/react', () => ({
  ...jest.requireActual('next-auth/react'),
  useSession: jest.fn(),
}))

jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
  ErrorDisplay: ({ title }: { title: string }) => <div>{title}</div>,
}))

describe('ProgramDetailsPage', () => {
  beforeEach(() => {
    capturedSetStatus = null
    ;(addToast as jest.Mock).mockClear()
    ;(handleAppError as jest.Mock).mockClear()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProgramDetailsData,
      loading: false,
      refetch: jest.fn(),
    })
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'test-user' } },
      status: 'authenticated',
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner when loading', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: true,
      data: null,
    })
    ;(useSession as jest.Mock).mockReturnValue({ data: null, status: 'loading' })

    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
    })
  })

  test('renders 404 if no program found', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: { managementProgram: null },
    })

    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Program Not Found')).toBeInTheDocument()
    })
  })

  test('renders program details correctly', async () => {
    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument()
      expect(screen.getByText('Sample summary')).toBeInTheDocument()
      expect(screen.getByText('Draft')).toBeInTheDocument()
      expect(screen.getByText('Jan 1, 2025')).toBeInTheDocument()
      expect(screen.getByText('Dec 31, 2025')).toBeInTheDocument()
      expect(screen.getByText('20')).toBeInTheDocument()
      expect(screen.getByText('Beginner, Intermediate')).toBeInTheDocument()
    })
  })

  test('renders program details correctly for a non-admin', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'non-admin' } },
      status: 'authenticated',
    })
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument()
      expect(screen.getByText('Sample summary')).toBeInTheDocument()
      expect(screen.getByText('Draft')).toBeInTheDocument()
      expect(screen.queryByRole('button', { name: /Program actions menu/ })).not.toBeInTheDocument()
    })
  })

  test('renders N/A if experienceLevels is null', async () => {
    const mockDataWithoutLevels = {
      managementProgram: { ...mockProgramDetailsData.managementProgram, experienceLevels: null },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: mockDataWithoutLevels,
    })
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('N/A')).toBeInTheDocument()
    })
  })

  describe('Admin Functionality', () => {
    const mockUpdateProgram = jest.fn()

    beforeEach(() => {
      ;(useSession as jest.Mock).mockReturnValue({
        data: { user: { login: 'admin-user' } }, // Matches admin in mock data
        status: 'authenticated',
      })
      ;(useMutation as unknown as jest.Mock).mockReturnValue([
        mockUpdateProgram,
        { loading: false },
      ])
    })

    test('successfully updates status from Draft to Published', async () => {
      mockUpdateProgram.mockResolvedValue({})
      render(<ProgramDetailsPage />)

      const actionsButton = await screen.findByRole('button', { name: /Program actions menu/ })
      fireEvent.click(actionsButton)

      const publishButton = await screen.findByRole('menuitem', { name: 'Publish' })
      fireEvent.click(publishButton)

      await waitFor(() => {
        expect(mockUpdateProgram).toHaveBeenCalledWith(
          expect.objectContaining({
            variables: {
              inputData: {
                key: 'test-program',
                name: 'Test Program',
                status: ProgramStatusEnum.Published,
              },
            },
          })
        )
      })
    })

    test('shows error toast when trying to update with invalid status', async () => {
      render(<ProgramDetailsPage />)

      await waitFor(() => {
        expect(screen.getByTestId('details-card')).toBeInTheDocument()
      })

      expect(capturedSetStatus).not.toBeNull()
      capturedSetStatus!('INVALID_STATUS')

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          color: 'danger',
          description: 'The provided status is not valid.',
          timeout: 3000,
          title: 'Invalid Status',
          variant: 'solid',
        })
        expect(mockUpdateProgram).not.toHaveBeenCalled()
      })
    })

    test('handles mutation error gracefully', async () => {
      const mockError = new Error('Mutation failed')
      mockUpdateProgram.mockRejectedValue(mockError)

      render(<ProgramDetailsPage />)

      const actionsButton = await screen.findByRole('button', { name: /Program actions menu/ })
      fireEvent.click(actionsButton)

      const publishButton = await screen.findByRole('menuitem', { name: 'Publish' })
      fireEvent.click(publishButton)

      await waitFor(() => {
        expect(mockUpdateProgram).toHaveBeenCalled()
        expect(handleAppError).toHaveBeenCalledWith(mockError)
      })
    })
  })

  test('renders program with null admins (uses undefined fallback)', async () => {
    const mockDataWithoutAdmins = {
      managementProgram: { ...mockProgramDetailsData.managementProgram, admins: null },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: mockDataWithoutAdmins,
    })
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument()
    })
  })

  test('renders program with null domains (uses undefined fallback)', async () => {
    const mockDataWithoutDomains = {
      managementProgram: { ...mockProgramDetailsData.managementProgram, domains: null },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: mockDataWithoutDomains,
    })
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument()
    })
  })

  test('renders program with null tags (uses undefined fallback)', async () => {
    const mockDataWithoutTags = {
      managementProgram: { ...mockProgramDetailsData.managementProgram, tags: null },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: mockDataWithoutTags,
    })
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument()
    })
  })

  test('calls addToast with permission denied when non-admin calls setStatus', async () => {
    const mockUpdateProgram = jest.fn()
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUpdateProgram, { loading: false }])
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'non-admin-user' } },
      status: 'authenticated',
    })

    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getByTestId('details-card')).toBeInTheDocument()
    })

    if (capturedSetStatus) {
      capturedSetStatus(ProgramStatusEnum.Published)
    }

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith({
        color: 'danger',
        description: 'Only admins can update the program status.',
        timeout: 3000,
        title: 'Permission Denied',
        variant: 'solid',
      })
    })
  })

  test('calls addToast with success when admin successfully updates status', async () => {
    const mockUpdateProgram = jest.fn().mockResolvedValue({})
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUpdateProgram, { loading: false }])
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })

    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getByTestId('details-card')).toBeInTheDocument()
    })

    if (capturedSetStatus) {
      capturedSetStatus(ProgramStatusEnum.Published)
    }

    await waitFor(() => {
      expect(mockUpdateProgram).toHaveBeenCalledWith(
        expect.objectContaining({
          variables: {
            inputData: {
              key: 'test-program',
              name: 'Test Program',
              status: ProgramStatusEnum.Published,
            },
          },
        })
      )
      expect(addToast).toHaveBeenCalledWith({
        title: 'Program status updated to Published',
        description: 'The status has been successfully updated.',
        variant: 'solid',
        color: 'success',
        timeout: 3000,
      })
    })
  })

  test('calls handleAppError when mutation fails', async () => {
    const mockError = new Error('Mutation failed')
    const mockUpdateProgram = jest.fn().mockRejectedValue(mockError)
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUpdateProgram, { loading: false }])
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'admin-user' } },
      status: 'authenticated',
    })

    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getByTestId('details-card')).toBeInTheDocument()
    })

    if (capturedSetStatus) {
      capturedSetStatus(ProgramStatusEnum.Published)
    }

    await waitFor(() => {
      expect(mockUpdateProgram).toHaveBeenCalled()
      expect(handleAppError).toHaveBeenCalledWith(mockError)
    })
  })

  test('renders program with minimal details ensuring default values are used', async () => {
    const mockDataWithNullFields = {
      managementProgram: {
        ...mockProgramDetailsData.managementProgram,
        status: null,
        startedAt: null,
        endedAt: null,
        menteesLimit: null,
        key: null,
        description: null,
        name: null,
      },
      managementProgramModules: [],
    }

    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: mockDataWithNullFields,
    })

    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getByTestId('details-card')).toBeInTheDocument()

      const detailsContent = screen.getByTestId('details-content')
      expect(detailsContent).toHaveTextContent('Mentees Limit0')
    })
  })
  it('renders mentee view when user gets forbidden error on management query', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: {
        user: { login: 'mentee1', isLeader: false, isMentor: false },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
    })
    const forbiddenError = {
      graphQLErrors: [{ message: 'Forbidden', extensions: { code: 'FORBIDDEN' } }],
      message: 'Forbidden',
    }
    const menteeData = {
      getProgram: {
        id: '1',
        key: 'gsoc-2025',
        name: 'GSoC 2025',
        description: 'Test program',
        status: 'ACTIVE',
        menteesLimit: null,
        experienceLevels: null,
        startedAt: '2025-01-01',
        endedAt: '2025-12-31',
        domains: null,
        tags: null,
        admins: [],
        recentMilestones: [],
      },
      getProgramModules: [],
    }
    ;(useQuery as unknown as jest.Mock).mockImplementation(
      (query: { kind?: string; definitions?: Array<{ name?: { value?: string } }> }) => {
        const opName = query?.definitions?.[0]?.name?.value ?? ''
        if (opName === 'GetManagementProgramAndModules') {
          return { data: null, loading: false, error: forbiddenError }
        }
        return { data: menteeData, loading: false, error: undefined }
      }
    )
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('GSoC 2025')).toBeInTheDocument()
    })
  })

  it('renders program not found for mentee with no enrolled program', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: {
        user: { login: 'mentee1', isLeader: false, isMentor: false },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
    })
    const forbiddenError = {
      graphQLErrors: [{ message: 'Forbidden', extensions: { code: 'FORBIDDEN' } }],
      message: 'Forbidden',
    }
    ;(useQuery as unknown as jest.Mock).mockImplementation(
      (query: { kind?: string; definitions?: Array<{ name?: { value?: string } }> }) => {
        const opName = query?.definitions?.[0]?.name?.value ?? ''
        if (opName === 'GetManagementProgramAndModules') {
          return { data: null, loading: false, error: forbiddenError }
        }
        return {
          data: { getProgram: null, getProgramModules: [] },
          loading: false,
          error: undefined,
        }
      }
    )
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText(/Program Not Found/i)).toBeInTheDocument()
    })
  })

  it('renders loading spinner while mentee data is loading', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: {
        user: { login: 'mentee1', isLeader: false, isMentor: false },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
    })
    const forbiddenError = {
      graphQLErrors: [{ message: 'Forbidden', extensions: { code: 'FORBIDDEN' } }],
      message: 'Forbidden',
    }
    ;(useQuery as unknown as jest.Mock).mockImplementation(
      (query: { kind?: string; definitions?: Array<{ name?: { value?: string } }> }) => {
        const opName = query?.definitions?.[0]?.name?.value ?? ''
        if (opName === 'GetManagementProgramAndModules') {
          return { data: null, loading: false, error: forbiddenError }
        }
        return { data: undefined, loading: true, error: undefined }
      }
    )
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(
        document.querySelector('svg') ||
          screen.queryByText(/loading/i) ||
          document.querySelector('[class*="spinner"]') ||
          document.querySelector('[class*="animate"]')
      ).toBeTruthy()
    })
  })
})
