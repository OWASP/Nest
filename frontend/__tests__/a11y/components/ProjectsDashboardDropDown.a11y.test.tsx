import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { FaFilter } from 'react-icons/fa6'
import ProjectsDashboardDropDown from 'components/ProjectsDashboardDropDown'

expect.extend(toHaveNoViolations)

const defaultProps = {
  buttonDisplayName: 'Filter',
  onAction: jest.fn(),
  selectedKeys: ['Active'],
  selectedLabels: ['Selected Item'],
  selectionMode: 'single' as 'single' | 'multiple',
  sections: [
    {
      title: 'Status',
      items: [
        { key: 'Active', label: 'Active' },
        { key: 'Inactive', label: 'Inactive' },
      ],
    },
    {
      title: 'Priority',
      items: [
        { key: 'High Priority', label: 'High Priority' },
        { key: 'Low Priority', label: 'Low Priority' },
      ],
    },
  ],
  icon: FaFilter,
  isOrdering: false,
}

describe('ProjectsDashboardDropDown a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ProjectsDashboardDropDown {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
