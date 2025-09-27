import { fireEvent, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { useSession as mockUseSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import { ProgramStatusEnum } from 'types/__generated__/graphql'
import ProgramActions from 'components/ProgramActions'

const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: () => ({ push: mockPush }),
}))

jest.mock('next-auth/react', () => {
  const actual = jest.requireActual('next-auth/react')
  return {
    ...actual,
    useSession: jest.fn(),
  }
})

describe('ProgramActions', () => {
  let setStatus: jest.Mock
  beforeEach(() => {
    setStatus = jest.fn()
    mockPush.mockClear()
  })

  beforeAll(async () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: {
        user: {
          name: 'Test User',
          email: 'test@example.com',
          login: 'testuser',
          isLeader: true,
        },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
      loading: false,
    })
  })

  test('renders and toggles dropdown', () => {
    render(<ProgramActions programKey="test-program" status="DRAFT" setStatus={setStatus} />)
    const button = screen.getByTestId('program-actions-button')
    fireEvent.click(button)
    expect(screen.getByText('Add Module')).toBeInTheDocument()
    expect(screen.getByText('Publish Program')).toBeInTheDocument()
    fireEvent.click(button)
    expect(screen.queryByText('Add Module')).not.toBeInTheDocument()
  })

  test('handles Add Module action', () => {
    render(<ProgramActions programKey="test-program" status="DRAFT" setStatus={setStatus} />)
    const button = screen.getByTestId('program-actions-button')
    fireEvent.click(button)
    fireEvent.click(screen.getByRole('menuitem', { name: /add module/i }))
    expect(mockPush).toHaveBeenCalled()
    expect(setStatus).not.toHaveBeenCalled()
  })

  test('handles Publish action', () => {
    render(<ProgramActions programKey="test-program" status="DRAFT" setStatus={setStatus} />)
    const button = screen.getByTestId('program-actions-button')
    fireEvent.click(button)
    fireEvent.click(screen.getByRole('menuitem', { name: /publish program/i }))
    expect(setStatus).toHaveBeenCalledWith(ProgramStatusEnum.Published)
    expect(mockPush).not.toHaveBeenCalled()
  })

  test('handles Move to Draft action', () => {
    render(<ProgramActions programKey="test-program" status="PUBLISHED" setStatus={setStatus} />)
    const button = screen.getByTestId('program-actions-button')
    fireEvent.click(button)
    fireEvent.click(screen.getByRole('menuitem', { name: /move to draft/i }))
    expect(setStatus).toHaveBeenCalledWith(ProgramStatusEnum.Draft)
  })

  test('handles Mark as Completed action', () => {
    render(<ProgramActions programKey="test-program" status="PUBLISHED" setStatus={setStatus} />)
    const button = screen.getByTestId('program-actions-button')
    fireEvent.click(button)
    fireEvent.click(screen.getByRole('menuitem', { name: /mark as completed/i }))
    expect(setStatus).toHaveBeenCalledWith(ProgramStatusEnum.Completed)
  })

  test('dropdown closes on outside click', () => {
    render(
      <div>
        <ProgramActions programKey="test-program" status="DRAFT" setStatus={setStatus} />
        <button data-testid="outside">Outside</button>
      </div>
    )
    const button = screen.getByTestId('program-actions-button')
    fireEvent.click(button)
    expect(screen.getByText('Add Module')).toBeInTheDocument()
    fireEvent.mouseDown(screen.getByTestId('outside'))
    expect(screen.queryByText('Add Module')).not.toBeInTheDocument()
  })
})
