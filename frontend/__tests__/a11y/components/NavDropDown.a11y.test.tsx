import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import type { Link as LinkType } from 'types/link'
import NavDropDown from 'components/NavDropDown'

const mockLink: LinkType = {
  text: 'Documentation',
  href: '/docs',
  submenu: [
    { text: 'Getting Started', href: '/docs/getting-started' },
    { text: 'API Reference', href: '/docs/api' },
    { text: 'Examples', href: '/docs/examples' },
  ],
}

const defaultProps = {
  pathname: '/current-page',
  link: mockLink,
}

describe('NavDropDown a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<NavDropDown {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when open', async () => {
    const { container } = render(<NavDropDown {...defaultProps} />)

    const button = screen.getByRole('button')
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Getting Started')).toBeInTheDocument()
    })

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
