import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import ModeToggle from 'components/ModeToggle'

jest.mock('next-themes', () => ({
  useTheme: () => ({ theme: 'light', setTheme: jest.fn() }),
}))

expect.extend(toHaveNoViolations)

describe('ModeToggle a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(<ModeToggle />)

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
