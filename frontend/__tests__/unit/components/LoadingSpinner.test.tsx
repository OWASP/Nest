import { render, screen } from '@testing-library/react'
import LoadingSpinner from '../LoadingSpinner'

// Mock next/image to avoid SSR-related issues during test runs
jest.mock('next/image', () => (props: any) => {
  // Replace <Image /> with a basic <img />
  return <img {...props} />
})

describe('<LoadingSpinner />', () => {
  it('renders without crashing', () => {
    render(<LoadingSpinner />)
    const images = screen.getAllByAltText('Loading indicator')
    expect(images.length).toBe(2) // One for light, one for dark
  })

  it('handles invalid imageUrl input gracefully', () => {
    render(<LoadingSpinner imageUrl={123 as any} />)
    const images = screen.getAllByAltText('Loading indicator')
    expect(images.length).toBe(2)
  })
  it('has appropriate alt text for accessibility', () => {
    render(<LoadingSpinner />)
    const images = screen.getAllByAltText('Loading indicator')
    expect(images.length).toBe(2)
  })
  it('applies correct Tailwind classes for dark/light mode', () => {
    render(<LoadingSpinner imageUrl="/test.png" />)
    const darkImage = screen.getByRole('img', { hidden: true })
    expect(darkImage).toHaveClass('dark:hidden')
  })

  it('renders default image if no imageUrl is provided', () => {
    render(<LoadingSpinner />)
    const images = screen.getAllByAltText('Loading indicator')
    expect(images[0].getAttribute('src')).toContain('white') // dark image
    expect(images[1].getAttribute('src')).toContain('black') // light image
  })

  it('renders custom image when imageUrl is provided', () => {
    const customUrl = '/img/spinner_white.png'
    render(<LoadingSpinner imageUrl={customUrl} />)
    const images = screen.getAllByAltText('Loading indicator')
    expect(images[0].getAttribute('src')).toContain('white') // dark image
    expect(images[1].getAttribute('src')).toContain('black') // light image
  })

  it('renders spinner container with correct styles', () => {
    render(<LoadingSpinner />)
    const spinnerContainer = screen.getByAltText('Loading indicator').closest('div')
    expect(spinnerContainer?.parentElement?.className).toContain('animate-fade-in-out')
  })

  it('has appropriate alt text and accessibility image role', () => {
    render(<LoadingSpinner />)
    const image = screen.getByAltText('Loading indicator')
    expect(image).toBeInTheDocument()
    expect(image.tagName.toLowerCase()).toBe('img')
  })
})
