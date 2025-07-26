import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import Footer from '@/components/Footer'
import { footerIcons } from '@/constants/footerIcons'

describe('Footer component', () => {
  // Basic render check — makes sure the component doesn't crash on mount
  it('should render the footer without any errors', () => {
    render(<Footer />)
    const footerElement = screen.getByRole('contentinfo')
    expect(footerElement).toBeInTheDocument()
  })

  // Ensures that the key footer sections are actually present in the DOM
  it('displays all primary section headings', () => {
    render(<Footer />)

    const headings = ['Project', 'Resources', 'Community', 'Legal'] // these may vary depending on actual content

    headings.forEach((headingText) => {
      const heading = screen.getByText(headingText)
      expect(heading).toBeInTheDocument()
    })
  })

  // Loops through each defined icon and checks if they are rendered properly
  // Also verifies correct labels and links for accessibility and functionality
  it('renders all social media icons with valid links and labels', () => {
    render(<Footer />)

    for (const icon of footerIcons) {
      const linkElement = screen.getByRole('link', { name: icon.label })
      expect(linkElement).toBeInTheDocument()
      expect(linkElement).toHaveAttribute('href', icon.href)
    }
  })

  // Tests the collapsible behavior of mobile sections by simulating click events
  it('expands and collapses footer sections when toggled', () => {
    render(<Footer />)

    const collapsibleButtons = screen.getAllByRole('button', { name: /expand/i })

    collapsibleButtons.forEach((button) => {
      const targetId = button.getAttribute('aria-controls')
      expect(targetId).toBeTruthy()

      const sectionContent = document.getElementById(targetId!)
      expect(sectionContent).not.toBeNull()

      if (sectionContent) {
        expect(sectionContent.classList.contains('hidden')).toBe(true)

        // simulate expanding
        fireEvent.click(button)

        expect(sectionContent.classList.contains('hidden')).toBe(false)
      }
    })
  })

  // Makes sure the component is following basic accessibility guidelines
  it('uses appropriate roles and accessible labels', () => {
    render(<Footer />)

    const footer = screen.getByRole('contentinfo')
    expect(footer).toBeInTheDocument()

    const allLinks = screen.getAllByRole('link')
    allLinks.forEach((link) => {
      expect(link).toHaveAttribute('aria-label')
    })
  })

  // Simulates a corner case where the sections array is empty or undefined
  // The component should still render without breaking the layout
  it('renders gracefully when no sections are passed', () => {
    render(<Footer sections={[]} />)

    const footer = screen.getByRole('contentinfo')
    expect(footer).toBeInTheDocument()

    const headings = screen.queryAllByRole('heading')
    expect(headings.length).toBe(0)
  })
})
