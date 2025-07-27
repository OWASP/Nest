describe('<Footer /> component', () => {
  beforeEach(() => {
    render(<Footer />)
  })

  // Test to ensure the footer component mounts without any error
  it('renders the footer component successfully', () => {
    expect(screen.getByTestId('footer')).toBeInTheDocument()
  })

  // Verifies that all section titles defined in the footer configuration appear
  it('displays all section titles from the footer configuration', () => {
    footerSections.forEach(section => {
      expect(screen.getByText(section.title)).toBeInTheDocument()
    })
  })

  // Simulates user interaction by clicking a section title to toggle its links
  it('shows and hides section links when the section is toggled', () => {
    const toggleButton = screen.getByRole('button', {
      name: footerSections[0].title,
    })
    fireEvent.click(toggleButton)

    footerSections[0].links.forEach(link => {
      expect(screen.getByText(link.text)).toBeInTheDocument()
    })

    fireEvent.click(toggleButton)

    footerSections[0].links.forEach(link => {
      expect(screen.queryByText(link.text)).not.toBeVisible()
    })
  })

  // Confirms each footer link appears with the correct display text and destination URL
  it('renders each footer link with the correct text and href value', () => {
    footerSections.forEach(section => {
      const toggleButton = screen.getByRole('button', { name: section.title })
      fireEvent.click(toggleButton)
      section.links.forEach(link => {
        const anchor = screen.getByRole('link', { name: link.text })
        expect(anchor).toHaveAttribute('href', link.href)
      })
    })
  })

  // Ensures that social media icons appear with the right accessible labels and URLs
  it('renders all social media icons with appropriate aria-labels and hrefs', () => {
    footerIcons.forEach(icon => {
      const iconLink = screen.getByLabelText(`OWASP Nest ${icon.label}`)
      expect(iconLink).toBeInTheDocument()
      expect(iconLink).toHaveAttribute('href', icon.href)
    })
  })

  // Validates that the version number is rendered from the environment configuration
  it('displays the release version passed from environment settings', () => {
    expect(screen.getByText('v1.2.3')).toBeInTheDocument()
  })

  // Checks that the footer shows the current year correctly in the copyright
  it('displays the correct current year in the copyright text', () => {
    const year = new Date().getFullYear()
    expect(
      screen.getByText(`© ${year} OWASP Nest. All rights reserved.`)
    ).toBeInTheDocument()
  })

  // Tests how the component handles a section object that has no links defined
  it('handles a section with no links without breaking the layout', () => {
    const emptySection = { title: 'Empty Section', links: [] }
    render(
      <footer>
        <button>{emptySection.title}</button>
      </footer>
    )
    expect(screen.getByText(emptySection.title)).toBeInTheDocument()
  })

  // Verifies that all interactive elements are accessible by screen readers
  it('ensures all buttons and links have accessible names for screen readers', () => {
    const allButtons = screen.getAllByRole('button')
    const allLinks = screen.getAllByRole('link')

    allButtons.forEach(btn => {
      expect(btn).toHaveAccessibleName()
    })

    allLinks.forEach(link => {
      expect(link).toHaveAccessibleName()
    })
  })

  // Checks that the main footer container applies the expected Tailwind class
  it('applies the correct class name for the footer container styling', () => {
    const footerContainer = screen.getByTestId('footer')
    expect(footerContainer).toHaveClass('bg-neutral-100')
  })
})
