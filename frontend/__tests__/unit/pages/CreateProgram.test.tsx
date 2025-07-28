import { useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { useProjectLeader } from 'hooks/useProjectLeader'
import { useRouter } from 'next/navigation'
import { render } from 'wrappers/testUtil'
import CreateProgramPage from 'app/mentorship/programs/create/page'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useMutation: jest.fn(),
}))

jest.mock('hooks/useProjectLeader')
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))
jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const mockRouterPush = jest.fn()
const mockCreateProgram = jest.fn()

describe('CreateProgramPage (no MockedProvider)', () => {
  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockRouterPush })
    ;(useMutation as jest.Mock).mockReturnValue([mockCreateProgram, { loading: false }])
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('redirects with toast if not a project leader', async () => {
    ;(useProjectLeader as jest.Mock).mockReturnValue({ isLeader: false, loading: false })

    render(<CreateProgramPage />)

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Access Denied' }))
      expect(mockRouterPush).toHaveBeenCalledWith('/mentorship/programs')
    })
  })

  test('renders form when session and leader are valid', async () => {
    ;(useProjectLeader as jest.Mock).mockReturnValue({ isLeader: true, loading: false })

    render(<CreateProgramPage />)
    expect(await screen.findByLabelText('Program Name *')).toBeInTheDocument()
  })

  test('submits form and redirects on success', async () => {
    ;(useProjectLeader as jest.Mock).mockReturnValue({ isLeader: true, loading: false })

    mockCreateProgram.mockResolvedValue({
      data: { createProgram: { key: 'program_1' } },
    })

    render(<CreateProgramPage />)

    fireEvent.change(screen.getByLabelText('Program Name *'), {
      target: { value: 'Test Program' },
    })
    fireEvent.change(screen.getByLabelText('Description *'), {
      target: { value: 'A description' },
    })
    fireEvent.change(screen.getByLabelText('Start Date *'), {
      target: { value: '2025-01-01' },
    })
    fireEvent.change(screen.getByLabelText('End Date *'), {
      target: { value: '2025-12-31' },
    })
    fireEvent.change(screen.getByLabelText('Tags'), {
      target: { value: 'tag1, tag2' },
    })
    fireEvent.change(screen.getByLabelText('Domains'), {
      target: { value: 'domain1, domain2' },
    })

    fireEvent.submit(screen.getByText('Save').closest('form')!)

    await waitFor(() => {
      expect(mockCreateProgram).toHaveBeenCalledWith({
        variables: {
          input: {
            name: 'Test Program',
            description: 'A description',
            menteesLimit: 5,
            startedAt: '2025-01-01',
            endedAt: '2025-12-31',
            tags: ['tag1', 'tag2'],
            domains: ['domain1', 'domain2'],
          },
        },
      })

      expect(mockRouterPush).toHaveBeenCalledWith('/my/mentorship')
    })
  })
})
