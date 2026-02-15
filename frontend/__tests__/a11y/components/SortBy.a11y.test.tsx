import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import SortBy from 'components/SortBy'

const defaultProps = {
  sortOptions: [
    { label: 'Name', key: 'name' },
    { label: 'Date', key: 'date' },
  ],
  selectedSortOption: 'name',
  onSortChange: jest.fn(),
  selectedOrder: 'asc',
  onOrderChange: jest.fn(),
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('SortBy a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(
      <main>
        <SortBy {...defaultProps} />
      </main>
    )

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
