import { useQuery, useMutation } from '@apollo/client/react'
import mockProgramDetailsData from '@mockData/mockProgramData'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { useSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import ProgramDetailsPage from 'app/my/mentorship/programs/[programKey]/page'
import '@testing-library/jest-dom'
import { ProgramStatusEnum } from 'types/__generated__/graphql'

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

describe('ProgramDetailsPage', () => {
  beforeEach(() => {
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
      data: { program: null },
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
      getProgram: { ...mockProgramDetailsData.getProgram, experienceLevels: null },
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
        expect(mockUpdateProgram).toHaveBeenCalledWith({
          variables: {
            inputData: {
              key: 'test-program',
              name: 'Test Program',
              status: ProgramStatusEnum.Published,
            },
          },
        })
      })
    })
  })
})
