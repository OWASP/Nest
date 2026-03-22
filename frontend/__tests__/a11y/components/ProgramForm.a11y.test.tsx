import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ProgramForm from 'components/ProgramForm'

jest.mock('@apollo/client/react', () => ({
  useApolloClient: jest.fn(() => ({
    query: jest.fn().mockResolvedValue({ data: { getMyPrograms: [] } }),
  })),
}))

const mockFormData = {
  name: 'Test Program',
  description: 'Test program description',
  menteesLimit: 10,
  startedAt: '2025-01-01',
  endedAt: '2025-06-01',
  tags: '',
  domains: '',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ProgramForm a11y ($name theme)', ({ theme }) => {
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
        <ProgramForm
          formData={mockFormData}
          setFormData={jest.fn()}
          onSubmit={jest.fn()}
          loading={false}
          title="Create Program"
        />
      </main>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
