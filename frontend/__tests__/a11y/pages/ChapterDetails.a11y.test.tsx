import { useQuery } from '@apollo/client/react'
import { mockChapterDetailsData } from '@mockData/mockChapterDetailsData'
import { render, screen, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ChapterDetailsPage from 'app/chapters/[chapterKey]/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  useParams: () => ({ chapterKey: 'test-chapter' }),
  usePathname: jest.fn(() => '/chapters/test-chapter'),
  useRouter: jest.fn(() => mockRouter),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ChapterDetailsPage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  const mockUseQuery = useQuery as unknown as jest.Mock

  it('should have no accessibility violations', async () => {
    mockUseQuery.mockReturnValue({
      data: mockChapterDetailsData,
      loading: false,
      error: null,
    })

    const { container } = render(<ChapterDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test City, Test Country')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when loading', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })
    const { container } = render(<ChapterDetailsPage />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when error occurs', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: new Error('graphql error'),
    })

    const { container } = render(<ChapterDetailsPage />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it("should have no accessibility violations when chapter doesn't exists", async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: null,
    })
    const { container } = render(<ChapterDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
