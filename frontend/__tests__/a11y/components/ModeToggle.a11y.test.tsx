import { render, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import ModeToggle from 'components/ModeToggle'

jest.mock('next-themes', () => ({
  useTheme: () => ({ theme: 'light', setTheme: jest.fn() }),
}))

describe('ModeToggle a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(<ModeToggle />)

    await screen.findByRole('button', { name: /Enable dark mode/i })

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
