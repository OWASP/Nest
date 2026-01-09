import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import SortBy from 'components/SortBy'

expect.extend(toHaveNoViolations)

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

describe('SortBy a11y', () => {
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
