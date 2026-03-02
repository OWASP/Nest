import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import SnapshotCard from 'components/SnapshotCard'

const defaultProps = {
  key: 'test-snapshot-1',
  title: 'Test Snapshot',
  button: { label: 'Open', onclick: jest.fn() },
  startAt: '2025-01-01T00:00:00Z',
  endAt: '2025-01-10T00:00:00Z',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('SnapshotCard a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<SnapshotCard {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
