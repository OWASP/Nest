import { mockChapterData } from '@mockData/mockChapterData'
import { screen, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
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

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ChaptersPage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
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
