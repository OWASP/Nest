import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { LabelList } from 'components/LabelList'

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('LabelList a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should have no accessibility violations with labels', async () => {
    const { container } = render(
      <LabelList entityKey="test-entity" labels={['bug', 'enhancement', 'docs']} />
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations with overflow labels', async () => {
    const { container } = render(
      <LabelList
        entityKey="test-entity"
        labels={['bug', 'enhancement', 'docs', 'a11y', 'ui', 'backend', 'testing']}
        maxVisible={3}
      />
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
