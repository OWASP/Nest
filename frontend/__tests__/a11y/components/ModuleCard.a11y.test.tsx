import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ModuleCard from 'components/ModuleCard'

const mockModules = [
  {
    id: '1',
    key: 'module-1',
    name: 'Intro to Web Security',
    description: 'A beginner module',
    experienceLevel: 'BEGINNER',
    startedAt: '2025-01-01',
    endedAt: '2025-03-01',
    mentors: [{ login: 'mentor1', name: 'Mentor One', avatarUrl: 'https://example.com/m1.png' }],
    mentees: [{ login: 'mentee1', name: 'Mentee One', avatarUrl: 'https://example.com/me1.png' }],
    tags: ['web'],
    domains: ['security'],
  },
]

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ModuleCard a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <main>
        <ModuleCard modules={mockModules as never[]} login="testuser" />
      </main>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
