import { mockChapterData } from '@mockData/mockChapterData'
import { screen, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import React from 'react'
import { render } from 'wrappers/testUtil'
import ChaptersPage from 'app/chapters/page'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('components/ChapterMapWrapper', () => {
  return () => <div></div>
})

jest.mock('components/SearchPageLayout', () => {
  return function MockPageLayout({ children }: { children: React.ReactNode }) {
    return <div>{children}</div>
  }
})

describe('ChaptersPage Accessibility', () => {
  it('should have no accessibility violations', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockChapterData.chapters,
      totalPages: 1,
    })

    const { container } = render(<ChaptersPage />)
    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
