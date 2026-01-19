import { mockCommitteeData } from '@mockData/mockCommitteeData'
import { screen, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import { render } from 'wrappers/testUtil'
import CommitteesPage from 'app/committees/page'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

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

describe('CommitteesPage Accessibility', () => {
  ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
    hits: mockCommitteeData.committees,
  })

  it('should have no accessibility violations', async () => {
    const { container } = render(<CommitteesPage />)

    await waitFor(() => {
      expect(screen.getByText('Committee 1')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
