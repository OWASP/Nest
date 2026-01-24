import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { FaUser } from 'react-icons/fa6'
import SecondaryCard from 'components/SecondaryCard'

const baseProps = {
  title: 'Test Title',
  icon: FaUser,
  children: <p>Test children</p>,
}

describe('SecondaryCard a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<SecondaryCard {...baseProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
