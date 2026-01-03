import { render, screen, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import ModeToggle from 'components/ModeToggle'

jest.mock('next-themes', () => ({
  useTheme: () => ({ theme: 'light', setTheme: jest.fn() }),
}))

expect.extend(toHaveNoViolations)

describe('ModeToggle a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<ModeToggle />)

    await waitFor(() => {
      expect(screen.getByRole('button')).toBeInTheDocument()
    })

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
