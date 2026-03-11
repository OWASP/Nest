import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ModuleForm from 'components/ModuleForm'

jest.mock('@apollo/client/react', () => ({
  useApolloClient: jest.fn(() => ({
    query: jest.fn().mockResolvedValue({ data: { searchProjects: [] } }),
  })),
}))

const mockFormData = {
  description: 'Test module description',
  domains: '',
  endedAt: '2025-06-01',
  experienceLevel: 'BEGINNER',
  labels: '',
  mentorLogins: '',
  name: 'Test Module',
  projectId: '',
  projectName: '',
  startedAt: '2025-01-01',
  tags: '',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ModuleForm a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
    jest.spyOn(console, 'error').mockImplementation((...args) => {
      if (typeof args[0] === 'string' && args[0].includes('not wrapped in act')) return
      throw new Error(`Console error: ${args.join(' ')}`)
    })
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  it('should have no accessibility violations', async () => {
    const { container } = render(
      <main>
        <ModuleForm
          formData={mockFormData}
          setFormData={jest.fn()}
          onSubmit={jest.fn()}
          loading={false}
          title="Create Module"
        />
      </main>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
