import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import Pagination from 'components/Pagination'

expect.extend(toHaveNoViolations)

const props = {
  currentPage: 1,
  totalPages: 5,
  isLoaded: true,
  onPageChange: jest.fn(),
}

describe('Pagination a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Pagination {...props} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
