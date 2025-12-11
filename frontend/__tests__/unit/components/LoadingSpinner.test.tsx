import { render, screen } from '@testing-library/react'
import LoadingSpinner from 'components/LoadingSpinner'

jest.mock('next/image', () => ({
  __esModule: true,
  // eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text
  default: (props) => <img {...props} />,
}))

describe('<LoadingSpinner />', () => {
  it('renders without crashing', () => {
    render(<LoadingSpinner />)
    const images = screen.getAllByAltText('Loading indicator')
    expect(images.length).toBe(2) // One for light, one for dark
  })

  it('handles invalid imageUrl input gracefully', () => {
    // With the original component, we test that it works with undefined/null
    render(<LoadingSpinner imageUrl={undefined} />)
    const images = screen.getAllByAltText('Loading indicator')
    expect(images.length).toBe(2)
    // Should fallback to default images when no valid input is provided
    expect(images[0].getAttribute('src')).toContain('white')
    expect(images[1].getAttribute('src')).toContain('blue')
  })
  it('has appropriate alt text for accessibility', () => {
    render(<LoadingSpinner />)
    const images = screen.getAllByAltText('Loading indicator')
    expect(images.length).toBe(2)
  })
  it('applies correct Tailwind classes for dark/light mode', () => {
    render(<LoadingSpinner imageUrl="/test.png" />)
    const images = screen.getAllByAltText('Loading indicator')

    // First image should be for dark mode (hidden in light, visible in dark)
    expect(images[0]).toHaveClass('hidden', 'rounded-full', 'dark:block')

    // Second image should be for light mode (visible in light, hidden in dark)
    expect(images[1]).toHaveClass('rounded-full', 'dark:hidden')
  })

  it('renders default image if no imageUrl is provided', () => {
    render(<LoadingSpinner />)
    const images = screen.getAllByAltText('Loading indicator')
    expect(images[0].getAttribute('src')).toContain('white') // dark image
    expect(images[1].getAttribute('src')).toContain('blue') // light image
  })

  it('renders custom image when imageUrl is provided', () => {
    const customUrl = '/img/spinner_white.png'
    render(<LoadingSpinner imageUrl={customUrl} />)
    const images = screen.getAllByAltText('Loading indicator')
    expect(images[0].getAttribute('src')).toBe(customUrl) // Should use the exact custom URL
    expect(images[1].getAttribute('src')).toBe('/img/spinner_blue.png') // Should transform white to blue
  })

  it('renders spinner container with correct styles', () => {
    render(<LoadingSpinner />)
    const fadeContainer = document.querySelector('.animate-fade-in-out')
    expect(fadeContainer).toBeInTheDocument()
    expect(fadeContainer?.className).toContain('animate-fade-in-out')
  })

  it('has appropriate alt text and accessibility image role', () => {
    render(<LoadingSpinner />)
    const images = screen.getAllByAltText('Loading indicator')
    expect(images[0]).toBeInTheDocument()
    expect(images[0].tagName.toLowerCase()).toBe('img')
    expect(images[1]).toBeInTheDocument()
    expect(images[1].tagName.toLowerCase()).toBe('img')
  })

  describe('Theme-specific image loading', () => {
    it('renders spinner_white.png for dark theme', () => {
      render(<LoadingSpinner />)
      const images = screen.getAllByAltText('Loading indicator')

      const darkThemeImage = images[0]
      expect(darkThemeImage).toHaveAttribute('src', '/img/spinner_white.png')
      expect(darkThemeImage).toHaveClass('hidden', 'rounded-full', 'dark:block')
    })

    it('renders spinner_blue.png for light theme', () => {
      render(<LoadingSpinner />)
      const images = screen.getAllByAltText('Loading indicator')

      const lightThemeImage = images[1]
      expect(lightThemeImage).toHaveAttribute('src', '/img/spinner_blue.png')
      expect(lightThemeImage).toHaveClass('rounded-full', 'dark:hidden')
    })

    it('uses correct theme images when custom imageUrl is provided', () => {
      const customUrl = '/img/spinner_white.png'
      render(<LoadingSpinner imageUrl={customUrl} />)
      const images = screen.getAllByAltText('Loading indicator')

      const darkThemeImage = images[0]
      expect(darkThemeImage).toHaveAttribute('src', customUrl)
      expect(darkThemeImage).toHaveClass('hidden', 'rounded-full', 'dark:block')

      const lightThemeImage = images[1]
      expect(lightThemeImage).toHaveAttribute('src', '/img/spinner_blue.png')
      expect(lightThemeImage).toHaveClass('rounded-full', 'dark:hidden')
    })
  })
})
