import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { FaFilter } from 'react-icons/fa6'
import ProjectsDashboardDropDown from 'components/ProjectsDashboardDropDown'

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

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ProjectsDashboardDropDown a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ProjectsDashboardDropDown {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
