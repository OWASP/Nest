import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { useSession } from 'next-auth/react'

import IssueCertificatePage from 'app/my/certificates/issue/page'
import { extractGraphQLErrors } from 'utils/helpers/handleGraphQLError'

const mockPush = jest.fn()
const mockIssueCertificate = jest.fn()

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useMutation: jest.fn(() => [mockIssueCertificate, { loading: false }]),
}))

jest.mock('@heroui/toast', () => ({ addToast: jest.fn() }))
jest.mock('next-auth/react', () => ({ useSession: jest.fn() }))
jest.mock('next/navigation', () => ({ useRouter: () => ({ push: mockPush }) }))
jest.mock('utils/helpers/handleGraphQLError', () => ({
  extractGraphQLErrors: jest.fn(() => ({ validationErrors: {}, hasValidationErrors: false })),
}))

jest.mock('components/AccessDeniedDisplay', () => ({
  __esModule: true,
  default: () => <div data-testid="access-denied" />,
}))
jest.mock('components/LoadingSpinner', () => ({
  __esModule: true,
  default: () => <div data-testid="loading-spinner" />,
}))
jest.mock('components/EntitySelectorInput', () => ({
  __esModule: true,
  default: ({
    entityType,
    value,
    onChange,
  }: {
    entityType: string
    value: string
    onChange: (v: string) => void
  }) => (
    <input
      data-testid={`entity-input-${entityType}`}
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}))
jest.mock('components/UserSelectorInput', () => ({
  __esModule: true,
  default: ({ onChange }: { onChange: (v: string[]) => void }) => (
    <button type="button" data-testid="add-user-btn" onClick={() => onChange(['testuser'])}>
      Add
    </button>
  ),
}))

describe('IssueCertificatePage', () => {
  const mockUseSession = useSession as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseSession.mockReturnValue({
      data: { user: { isLeader: true } },
      status: 'authenticated',
    })
  })

  it('handles authentication loading, login redirect, access control, and banner dismissal', () => {
    mockUseSession.mockReturnValueOnce({ data: null, status: 'loading' })
    const { rerender } = render(<IssueCertificatePage />)
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()

    mockUseSession.mockReturnValueOnce({ data: null, status: 'unauthenticated' })
    rerender(<IssueCertificatePage />)
    expect(mockPush).toHaveBeenCalledWith('/auth/login')

    mockUseSession.mockReturnValueOnce({
      data: { user: { isLeader: false } },
      status: 'authenticated',
    })
    rerender(<IssueCertificatePage />)
    expect(screen.getByTestId('access-denied')).toBeInTheDocument()

    mockUseSession.mockReturnValue({ data: { user: { isLeader: true } }, status: 'authenticated' })
    rerender(<IssueCertificatePage />)

    fireEvent.click(screen.getByRole('button', { name: 'Dismiss notice' }))
  })

  it('handles form validation, GraphQL errors, submission rejections, and successful issuance', async () => {
    mockIssueCertificate.mockResolvedValue({ data: { issueCertificate: { success: true } } })

    render(<IssueCertificatePage />)

    const titleInput = screen.getByLabelText(/Certificate Title/)
    const messageInput = screen.getByLabelText(/Certificate Body Message/)
    const projectInput = screen.getByTestId('entity-input-project')
    const chapterInput = screen.getByTestId('entity-input-chapter')
    const submitBtn = screen.getByRole('button', { name: 'Issue Certificates' })
    const addUserBtn = screen.getByTestId('add-user-btn')

    fireEvent.change(titleInput, { target: { value: 'A'.repeat(51) } })
    fireEvent.click(submitBtn)

    fireEvent.change(titleInput, { target: { value: 'Valid Title' } })
    fireEvent.change(messageInput, { target: { value: 'B'.repeat(281) } })
    fireEvent.click(submitBtn)

    fireEvent.change(messageInput, { target: { value: 'Valid Message' } })
    fireEvent.click(addUserBtn)
    fireEvent.click(submitBtn)

    fireEvent.change(projectInput, { target: { value: 'nest' } })
    fireEvent.change(chapterInput, { target: { value: 'london' } })
    fireEvent.click(submitBtn)

    mockIssueCertificate.mockRejectedValueOnce(new Error('Validation failed'))
    ;(extractGraphQLErrors as jest.Mock).mockReturnValueOnce({
      validationErrors: { title: 'Title already exists' },
      hasValidationErrors: true,
    })
    fireEvent.change(chapterInput, { target: { value: '' } })
    await act(async () => {
      fireEvent.click(submitBtn)
    })

    fireEvent.change(titleInput, { target: { value: 'New Title' } })

    mockIssueCertificate.mockRejectedValueOnce(new Error('Server failure'))
    await act(async () => {
      fireEvent.click(submitBtn)
    })

    mockIssueCertificate.mockRejectedValueOnce('String rejection')
    await act(async () => {
      fireEvent.click(submitBtn)
    })

    mockIssueCertificate.mockResolvedValueOnce({ data: { issueCertificate: { success: true } } })
    await act(async () => {
      fireEvent.click(submitBtn)
    })
    await waitFor(() => {
      expect(mockIssueCertificate).toHaveBeenCalledWith({
        variables: {
          inputData: {
            recipientLogins: ['testuser'],
            title: 'New Title',
            message: 'Valid Message',
            projectKey: 'nest',
            chapterKey: null,
          },
        },
      })
    })

    fireEvent.change(titleInput, { target: { value: 'Chapter Title' } })
    fireEvent.change(projectInput, { target: { value: '' } })
    fireEvent.change(chapterInput, { target: { value: 'london' } })
    fireEvent.click(addUserBtn)

    await act(async () => {
      fireEvent.click(submitBtn)
    })
    await waitFor(() => {
      expect(mockIssueCertificate).toHaveBeenCalledWith({
        variables: {
          inputData: {
            recipientLogins: ['testuser'],
            title: 'Chapter Title',
            message: expect.any(String),
            projectKey: null,
            chapterKey: 'london',
          },
        },
      })
    })
  })
})
