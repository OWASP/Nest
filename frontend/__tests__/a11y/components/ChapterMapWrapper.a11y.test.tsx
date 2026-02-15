import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ChapterMapWrapper from 'components/ChapterMapWrapper'

jest.mock('next/dynamic', () => () => {
  const MockChapterMap = () => <div data-testid="chapter-map" />
  MockChapterMap.displayName = 'MockChapterMap'
  return MockChapterMap
})

const mockChapters = [
  {
    key: 'chapter-1',
    name: 'Test Chapter',
    suggestedLocation: 'Test Location',
    _geoloc: { lat: 0, lng: 0 },
  },
]

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ChapterMapWrapper a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <ChapterMapWrapper
        geoLocData={mockChapters as never[]}
        showLocal={false}
        style={{ width: '100%', height: '400px' }}
      />
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
