import { fireEvent, render, screen } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import Footer from 'components/Footer'

expect.extend(toHaveNoViolations)

jest.mock('next/link', () => {
  return function MockedLink({ children, href, ...props }) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

describe('Footer a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Footer />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when section is opened', async () => {
    const { container } = render(<Footer />)

    const button = screen.getByTestId('footer-section-button-Resources')
    fireEvent.click(button)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
