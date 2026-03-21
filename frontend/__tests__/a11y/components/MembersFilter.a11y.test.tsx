import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import MembersFilter from 'components/MembersFilter'

const defaultProps = {
  selectedAffinity: 'all',
  onAffinityChange: jest.fn(),
  selectedMemberTypes: ['all'],
  onMemberTypesChange: jest.fn(),
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('MembersFilter a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(
      <main>
        <MembersFilter {...defaultProps} />
      </main>
    )

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
