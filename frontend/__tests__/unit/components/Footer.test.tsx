import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { Footer } from '@/components/Footer'
import { footerSections, footerIcons } from '@/config/footerConfig'

// Mock the release version to make the test predictable
jest.mock('../../../src/config/environment', () => ({
  RELEASE_VERSION: 'v1.2.3',
}))

describe('<Footer />', () => {
  // Just checking if the footer renders without crashing
  it('renders the footer component', () => {
    render(<Footer />)
    expect(screen.getByText('Nest')).toBeInTheDocument()
  })

  // Make sure all footer section titles (like "Docs", "Community") show up
  it('renders all footer sections', () => {
    render(<Footer />)
    footerSections.forEach(section => {
      expect(screen.getByText(section.title)).toBeInTheDocument()
    })
  })

  // Check if all the social icons (Twitter, GitHub, etc.) are there
  it('renders the social media icons', () => {
    render(<Footer />)
    footerIcons.forEach(icon => {
      expect(screen.getByRole('link', { name: icon.label })).toBeInTheDocument()
    })
  })

  // Test the behavior of toggling a section open and closed
  it('shows and hides section links when the section is toggled', () => {
    render(<Footer />)

    // Pick the first section that has actual links (just to be safe)
    const sectionWithLinks = footerSections.find(section => section.links.length > 0)
    if (!sectionWithLinks) {
      throw new Error('No footer section with links found for testing')
    }

    // Click to expand the section
    const toggleButton = screen.getByRole('button', {
      name: sectionWithLinks.title,
    })
    fireEvent.click(toggleButton)

    // Now the links inside should show up
    sectionWithLinks.links.forEach(link => {
      expect(screen.getByText(link.text)).toBeInTheDocument()
    })

    // Click again to collapse the section
    fireEvent.click(toggleButton)

    // Now those links should be gone (not just hidden — removed from DOM)
    sectionWithLinks.links.forEach(link => {
      expect(screen.queryByText(link.text)).not.toBeInTheDocument()
    })
  })

  // This checks that the version number (from env config) is displayed
  it('renders version number from environment variable', () => {
    render(<Footer />)
    expect(screen.getByText(/v1.2.3/)).toBeInTheDocument()
  })

  // Confirm that if we ever have an empty section, the layout doesn't break
  it('handles a section with no links without breaking the layout', () => {
    const mockSections = [...footerSections, { title: 'Empty Section', links: [] }]

    // Temporarily override the footerSections for this test
    jest
      .spyOn(require('../../../src/config/footerConfig'), 'footerSections', 'get')
      .mockReturnValue(mockSections)

    render(<Footer />)
    expect(screen.getByText('Empty Section')).toBeInTheDocument()
  })
})
