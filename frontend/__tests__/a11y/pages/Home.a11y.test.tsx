import { useQuery } from '@apollo/client/react'
import { mockAlgoliaData, mockGraphQLData } from '@mockData/mockHomeData'
import { render, screen, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import Home from 'app/page'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('@/components/MarkdownWrapper', () => {
  return ({ content, className }: { content: string; className?: string }) => (
    <div
      className={`md-wrapper ${className || ''}`}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  )
})

jest.mock('components/Modal', () => {
  const ModalMock = jest.fn(({ isOpen, onClose, title, summary, button, description }) => {
    if (!isOpen) return null
    return (
      <dialog open>
        <h2>{title}</h2>
        <p>{summary}</p>
        <p>{description}</p>
        <button onClick={onClose} aria-label="Close modal">
          Close
        </button>
        <a href={button.url}>{button.label}</a>
      </dialog>
    )
  })
  return ModalMock
})

describe('HomePage Accessibility', () => {
  afterAll(() => {
    jest.clearAllMocks()
  })

  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockGraphQLData,
      loading: false,
      error: null,
    })
    ;(fetchAlgoliaData as jest.Mock).mockReturnValue(mockAlgoliaData)

    const { container } = render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Welcome to OWASP Nest')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
