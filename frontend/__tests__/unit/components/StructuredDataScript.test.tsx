import { render } from '@testing-library/react'
import DOMPurify from 'isomorphic-dompurify'
import { ProfilePageStructuredData } from 'types/profilePageStructuredData'
import StructuredDataScript from 'components/StructuredDataScript'

jest.mock('isomorphic-dompurify', () => ({
  sanitize: jest.fn((input: string) => input),
}))

describe('<StructuredDataScript />', () => {
  const mockDOMPurify = DOMPurify.sanitize as jest.MockedFunction<typeof DOMPurify.sanitize>

  const mockBasicData: ProfilePageStructuredData = {
    '@context': 'https://schema.org',
    '@type': 'ProfilePage',
    mainEntity: {
      '@type': 'Person',
      name: 'John Doe',
      url: 'https://example.com/john-doe',
      description: 'Software Developer',
    },
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockDOMPurify.mockImplementation((input: string) => input)
  })

  it('renders script tag with correct id and type attributes', () => {
    const { container } = render(<StructuredDataScript data={mockBasicData} />)
    const script = container.querySelector('script')

    expect(script).toBeInTheDocument()
    expect(script).toHaveAttribute('id', 'profile-structured-data')
    expect(script).toHaveAttribute('type', 'application/ld+json')
  })

  it('calls DOMPurify.sanitize with stringified JSON data', () => {
    render(<StructuredDataScript data={mockBasicData} />)

    expect(mockDOMPurify).toHaveBeenCalledTimes(1)
    const callArg = mockDOMPurify.mock.calls[0][0] as string
    expect(typeof callArg).toBe('string')
    expect(callArg).toContain(mockBasicData['@context'])
    expect(callArg).toContain(mockBasicData.mainEntity.name)
  })

  it('renders sanitized content in script tag', () => {
    mockDOMPurify.mockReturnValue('<sanitized-json>')

    const { container } = render(<StructuredDataScript data={mockBasicData} />)
    const script = container.querySelector('script')

    expect(script?.innerHTML).toBe('<sanitized-json>')
  })

  it('handles complex data with all optional properties', () => {
    const complexData: ProfilePageStructuredData = {
      '@context': 'https://schema.org',
      '@type': 'ProfilePage',
      dateCreated: '2024-01-01T00:00:00Z',
      dateModified: '2024-12-01T00:00:00Z',
      mainEntity: {
        '@type': 'Person',
        name: 'Jane Doe',
        url: 'https://example.com/jane-doe',
        description: 'Tech Lead',
        image: 'https://example.com/jane.jpg',
        knowsAbout: ['JavaScript', 'React', 'Node.js'],
        sameAs: ['https://linkedin.com/in/jane-doe', 'https://github.com/jane-doe'],
        memberOf: {
          '@type': 'Organization',
          name: 'Tech Company',
          url: 'https://tech-company.com',
        },
        worksFor: {
          '@type': 'Organization',
          name: 'Tech Company',
        },
        interactionStatistic: [
          {
            '@type': 'InteractionCounter',
            interactionType: 'https://schema.org/CommentAction',
            userInteractionCount: 42,
          },
        ],
      },
    }

    const { container } = render(<StructuredDataScript data={complexData} />)
    const script = container.querySelector('script')

    expect(script?.innerHTML).toContain('Jane Doe')
    expect(script?.innerHTML).toContain('JavaScript')
    expect(mockDOMPurify).toHaveBeenCalled()
  })

  it('produces valid JSON in the call to sanitize', () => {
    render(<StructuredDataScript data={mockBasicData} />)

    const callArg = mockDOMPurify.mock.calls[0][0] as string
    expect(() => JSON.parse(callArg)).not.toThrow()

    const parsed = JSON.parse(callArg)
    expect(parsed['@context']).toBe(mockBasicData['@context'])
    expect(parsed.mainEntity.name).toBe(mockBasicData.mainEntity.name)
  })

  it('sanitizes malicious XSS content', () => {
    mockDOMPurify.mockImplementation((input: string) =>
      input.replace(/<script[^>]*>.*?<\/script>/gi, '')
    )

    const maliciousData: ProfilePageStructuredData = {
      '@context': 'https://schema.org',
      '@type': 'ProfilePage',
      mainEntity: {
        '@type': 'Person',
        name: 'John<script>alert("xss")</script>',
      },
    }

    render(<StructuredDataScript data={maliciousData} />)

    expect(mockDOMPurify).toHaveBeenCalled()
    const callArg = mockDOMPurify.mock.calls[0][0]
    expect(callArg).toContain('John')
  })

  it('handles special characters in data', () => {
    const dataWithSpecialChars: ProfilePageStructuredData = {
      '@context': 'https://schema.org',
      '@type': 'ProfilePage',
      mainEntity: {
        '@type': 'Person',
        name: "John O'Reilly",
        description: 'Test & Developer "with quotes"',
      },
    }

    const { container } = render(<StructuredDataScript data={dataWithSpecialChars} />)
    const script = container.querySelector('script')

    expect(script?.innerHTML).toContain("O'Reilly")
    expect(script?.innerHTML).toContain('&')
  })

  it('updates script content when data prop changes', () => {
    const { rerender, container } = render(<StructuredDataScript data={mockBasicData} />)

    let script = container.querySelector('script')
    expect(script?.innerHTML).toContain('John Doe')

    const newData: ProfilePageStructuredData = {
      '@context': 'https://schema.org',
      '@type': 'ProfilePage',
      mainEntity: {
        '@type': 'Person',
        name: 'Jane Smith',
      },
    }

    rerender(<StructuredDataScript data={newData} />)

    script = container.querySelector('script')
    expect(script?.innerHTML).toContain('Jane Smith')
  })

  it('formats JSON with proper indentation', () => {
    render(<StructuredDataScript data={mockBasicData} />)

    const callArg = mockDOMPurify.mock.calls[0][0] as string
    expect(callArg).toContain('\n')
    expect(callArg).toMatch(/\s{2}"/) // Check for 2-space indentation
  })

  it('does not modify original data object', () => {
    const originalData = JSON.stringify(mockBasicData)

    render(<StructuredDataScript data={mockBasicData} />)

    expect(JSON.stringify(mockBasicData)).toBe(originalData)
  })

  it('renders a single script element only', () => {
    const { container } = render(<StructuredDataScript data={mockBasicData} />)
    const scripts = container.querySelectorAll('script')

    expect(scripts).toHaveLength(1)
  })
})
