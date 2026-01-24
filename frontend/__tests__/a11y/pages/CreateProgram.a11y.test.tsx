import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useSession } from 'next-auth/react'
import CreateProgramPage from 'app/my/mentorship/programs/create/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({ programKey: 'test-program' })),
  useRouter: jest.fn(() => ({ push: jest.fn() })),
}))

jest.mock('@apollo/client/react', () => ({
  useMutation: jest.fn(),
  useQuery: jest.fn(),
  useApolloClient: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

describe('CreateProgramPage Accessibility', () => {
  ;(useApolloClient as jest.Mock).mockReturnValue({
    query: jest.fn().mockReturnValue({
      data: {
        searchProjects: [{ id: '123', name: 'Awesome Project' }],
      },
    }),
  })
  ;(useSession as jest.Mock).mockReturnValue({
    data: { user: { login: 'admin-user', isProjectLeader: true } },
    status: 'authenticated',
  })
  ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])
  ;(useQuery as unknown as jest.Mock).mockReturnValue({
    data: {
      getProgram: {
        admins: [{ login: 'admin-user' }],
      },
    },
    loading: false,
  })

  it('should have no accessibility violations', async () => {
    const { container } = render(<CreateProgramPage />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
