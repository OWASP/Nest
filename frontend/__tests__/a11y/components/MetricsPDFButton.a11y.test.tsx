import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import MetricsPDFButton from 'components/MetricsPDFButton'

jest.mock('server/fetchMetricsPDF', () => ({
  fetchMetricsPDF: jest.fn(),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('MetricsPDFButton a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <main>
        <MetricsPDFButton path="/metrics/test" fileName="test-metrics.pdf" />
      </main>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
