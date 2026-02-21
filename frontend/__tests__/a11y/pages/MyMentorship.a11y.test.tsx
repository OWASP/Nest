import { useQuery } from '@apollo/client/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { render } from 'wrappers/testUtil'
import MyMentorshipPage from 'app/my/mentorship/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

const mockProgramData = {
  myPrograms: {
    programs: [
      {
        id: '1',
        key: 'program-1',
        name: 'Test Program',
        description: 'Test Description',
        status: 'draft',
        startedAt: '2025-07-28',
        endedAt: '2025-08-10',
        experienceLevels: ['beginner'],
        menteesLimit: 10,
        admins: [],
      },
    ],
    totalPages: 1,
  },
}

jest.mock('hooks/useUpdateProgramStatus', () => ({
  useUpdateProgramStatus: () => ({ updateProgramStatus: jest.fn() }),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('MyMentorshipPage ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProgramData,
      loading: false,
      error: null,
    })

    const { container } = render(<MyMentorshipPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
