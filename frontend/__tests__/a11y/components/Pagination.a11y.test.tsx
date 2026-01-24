import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import Pagination from 'components/Pagination'

const props = {
  currentPage: 6,
  totalPages: 10,
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
