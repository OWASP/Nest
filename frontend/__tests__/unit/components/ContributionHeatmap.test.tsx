import { useQuery } from '@apollo/client/react'
import { screen, waitFor } from '@testing-library/react'
import { mockUserDetailsData } from '@unit/data/mockUserDetails'
import React from 'react'
import { render } from 'wrappers/testUtil'
import UserDetailsPage from 'app/members/[memberKey]/page'
import { drawContributions, fetchHeatmapData } from 'utils/helpers/githubHeatmap'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useParams: () => ({ memberKey: 'test-user' }),
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}))

jest.mock('utils/helpers/githubHeatmap', () => ({
  fetchHeatmapData: jest.fn(),
  drawContributions: jest.fn(() => {}),
}))

// Render Next/Image as a regular <img> to inspect src/alt
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: React.ComponentProps<'img'>) => {
    // eslint-disable-next-line jsx-a11y/alt-text, @next/next/no-img-element
    return <img {...props} />
  },
}))

// Theme mock that we can toggle between tests and rerenders
let currentTheme: 'light' | 'dark' = 'light'
jest.mock('next-themes', () => ({
  useTheme: () => ({ resolvedTheme: currentTheme }),
}))

// Minimal canvas stubs for jsdom
// Store original methods to restore after tests
const originalGetContext = HTMLCanvasElement.prototype.getContext
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL

beforeAll(() => {
  Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
    value: jest.fn(() => ({
      // 2d context stubs if needed later
      fillRect: jest.fn(),
      clearRect: jest.fn(),
      getImageData: jest.fn(() => ({ data: [] })),
      putImageData: jest.fn(),
      createImageData: jest.fn(() => []),
      setTransform: jest.fn(),
      drawImage: jest.fn(),
      save: jest.fn(),
      fillText: jest.fn(),
      restore: jest.fn(),
      beginPath: jest.fn(),
      moveTo: jest.fn(),
      lineTo: jest.fn(),
      closePath: jest.fn(),
      stroke: jest.fn(),
      translate: jest.fn(),
      scale: jest.fn(),
      rotate: jest.fn(),
      arc: jest.fn(),
      fill: jest.fn(),
      measureText: jest.fn(() => ({ width: 0 })),
    })),
    writable: true,
    configurable: true,
  })

  Object.defineProperty(HTMLCanvasElement.prototype, 'toDataURL', {
    value: jest.fn(() => 'data:image/png;base64,heatmap'),
    writable: true,
    configurable: true,
  })
})

afterAll(() => {
  Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
    value: originalGetContext,
    writable: true,
    configurable: true,
  })

  Object.defineProperty(HTMLCanvasElement.prototype, 'toDataURL', {
    value: originalToDataURL,
    writable: true,
    configurable: true,
  })
})

describe('ContributionHeatmap behavior (via UserDetailsPage)', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      loading: false,
      error: null,
    })
    ;(drawContributions as jest.Mock).mockClear()
    ;(fetchHeatmapData as jest.Mock).mockReset()
    currentTheme = 'light'
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering with minimal required props', () => {
    test('renders fallback background when no contributions data', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({})

      render(<UserDetailsPage />)

      await waitFor(() => {
        const bg = screen.getByAltText('Heatmap Background')
        expect(bg).toBeInTheDocument()
        const container = bg.closest(String.raw`div.hidden.lg\:block`)
        expect(container).toBeInTheDocument()
      })
      expect(drawContributions).not.toHaveBeenCalled()
    })

    test('renders successfully with user data but no heatmap data', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({})

      render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument()
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })
    })
  })

  describe('Conditional rendering logic', () => {
    test('does not render heatmap section when user is private contributor (null response)', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue(null)

      render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.queryByAltText('Heatmap Background')).toBeNull()
        expect(screen.queryByAltText('Contribution Heatmap')).toBeNull()
      })
    })

    test('shows heatmap container only when not private contributor', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 5, intensity: 2 }],
        years: [{ year: '2025' }],
      })

      render(<UserDetailsPage />)

      await waitFor(() => {
        const container = screen
          .getByAltText('Heatmap Background')
          .closest(String.raw`div.hidden.lg\:block`)
        expect(container).toBeInTheDocument()
      })
    })
  })

  describe('Prop-based behavior', () => {
    test('uses dark placeholder image in dark mode without data', async () => {
      currentTheme = 'dark'
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({})

      render(<UserDetailsPage />)

      await waitFor(() => {
        const bg = screen.getByAltText('Heatmap Background') as HTMLImageElement
        expect(bg).toBeInTheDocument()
        expect(bg.src).toContain('heatmap-background-dark.png')
      })
    })

    test('uses light placeholder image in light mode without data', async () => {
      currentTheme = 'light'
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({})

      render(<UserDetailsPage />)

      await waitFor(() => {
        const bg = screen.getByAltText('Heatmap Background') as HTMLImageElement
        expect(bg).toBeInTheDocument()
        expect(bg.src).toContain('heatmap-background-light.png')
      })
    })

    test('passes correct theme parameter to drawContributions', async () => {
      currentTheme = 'light'
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 1, intensity: 1 }],
        years: [{ year: '2025' }],
      })

      const { rerender } = render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })

      currentTheme = 'dark'
      rerender(<UserDetailsPage />)

      await waitFor(() => {
        expect((drawContributions as jest.Mock).mock.calls.length).toBeGreaterThan(0)
      })

      const lastCallArgs = (drawContributions as jest.Mock).mock.calls.at(-1)
      expect(lastCallArgs?.[1]?.themeName).toBe('dark')
    })
  })

  describe('State changes and internal logic', () => {
    test('draws and shows contribution heatmap image after theme change when data available', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 1, intensity: 1 }],
        years: [{ year: '2025' }],
      })

      const { rerender } = render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })

      currentTheme = 'dark'
      rerender(<UserDetailsPage />)

      await waitFor(() => {
        const img = screen.getByAltText('Contribution Heatmap')
        expect(img).toBeInTheDocument()
      })

      expect(drawContributions).toHaveBeenCalled()
      const lastCallArgs = (drawContributions as jest.Mock).mock.calls.at(-1)
      expect(lastCallArgs?.[1]?.themeName).toBe('dark')
    })

    test('transitions from fallback to rendered heatmap on theme toggle', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 10, intensity: 3 }],
        years: [{ year: '2025' }],
      })

      const { rerender } = render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })

      currentTheme = 'dark'
      rerender(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Contribution Heatmap')).toBeInTheDocument()
        expect(screen.queryByAltText('Heatmap Background')).toBeNull()
      })
    })
  })

  describe('Default values and fallbacks', () => {
    test('shows loading placeholder when heatmap data exists but image not generated yet', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [],
        years: [],
      })

      render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })
    })

    test('handles empty contributions array gracefully', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [],
        years: [],
      })

      render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })
      expect(drawContributions).not.toHaveBeenCalled()
    })
  })

  describe('Text and content rendering', () => {
    test('renders with correct alt text for background image', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({})

      render(<UserDetailsPage />)

      await waitFor(() => {
        const bg = screen.getByAltText('Heatmap Background')
        expect(bg).toHaveAttribute('alt', 'Heatmap Background')
      })
    })

    test('renders with correct alt text for generated heatmap image', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 1, intensity: 1 }],
        years: [{ year: '2025' }],
      })

      const { rerender } = render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })

      currentTheme = 'dark'
      rerender(<UserDetailsPage />)

      await waitFor(() => {
        const img = screen.getByAltText('Contribution Heatmap')
        expect(img).toHaveAttribute('alt', 'Contribution Heatmap')
      })
    })
  })

  describe('Edge cases and invalid inputs', () => {
    test('handles undefined contributions data', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue(undefined)

      render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.queryByAltText('Heatmap Background')).toBeNull()
        expect(screen.queryByAltText('Contribution Heatmap')).toBeNull()
      })
    })

    test('handles malformed heatmap data structure', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: 'invalid',
        years: null,
      })

      render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument()
      })
    })

    test('handles empty years array', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 5, intensity: 2 }],
        years: [],
      })

      render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })
    })
  })

  describe('Accessibility', () => {
    test('canvas element is hidden from accessibility tree', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 1, intensity: 1 }],
        years: [{ year: '2025' }],
      })

      const { rerender } = render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })

      currentTheme = 'dark'
      rerender(<UserDetailsPage />)

      await waitFor(() => {
        const canvas = document.querySelector('canvas')
        expect(canvas).toHaveAttribute('aria-hidden', 'true')
      })
    })

    test('heatmap image has proper alt text for screen readers', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 1, intensity: 1 }],
        years: [{ year: '2025' }],
      })

      const { rerender } = render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })

      currentTheme = 'dark'
      rerender(<UserDetailsPage />)

      await waitFor(() => {
        const img = screen.getByAltText('Contribution Heatmap')
        expect(img).toHaveAccessibleName()
      })
    })
  })

  describe('DOM structure and styling', () => {
    test('heatmap container has correct responsive classes', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 1, intensity: 1 }],
        years: [{ year: '2025' }],
      })

      render(<UserDetailsPage />)

      await waitFor(() => {
        const container = screen
          .getByAltText('Heatmap Background')
          .closest(String.raw`div.hidden.lg\:block`)
        expect(container).toHaveClass('hidden')
        expect(container).toHaveClass('lg:block')
      })
    })

    test('heatmap background has correct styling classes', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({})

      render(<UserDetailsPage />)

      await waitFor(() => {
        const bg = screen.getByAltText('Heatmap Background') as HTMLImageElement
        expect(bg).toHaveClass('heatmap-background-loader')
        expect(bg).toHaveClass('h-full')
        expect(bg).toHaveClass('w-full')
        expect(bg).toHaveClass('object-cover')
      })
    })

    test('rendered heatmap image has correct styling classes', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 1, intensity: 1 }],
        years: [{ year: '2025' }],
      })

      const { rerender } = render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })

      currentTheme = 'dark'
      rerender(<UserDetailsPage />)

      await waitFor(() => {
        const img = screen.getByAltText('Contribution Heatmap') as HTMLImageElement
        expect(img).toHaveClass('h-full')
        expect(img).toHaveClass('w-full')
        expect(img).toHaveClass('object-cover')
      })
    })

    test('canvas is hidden with display none', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 1, intensity: 1 }],
        years: [{ year: '2025' }],
      })

      const { rerender } = render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })

      currentTheme = 'dark'
      rerender(<UserDetailsPage />)

      await waitFor(() => {
        const canvas = document.querySelector('canvas')
        expect(canvas).toHaveStyle({ display: 'none' })
      })
    })
  })

  describe('Integration with drawContributions', () => {
    test('calls drawContributions with canvas reference', async () => {
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
        contributions: [{ date: '2025-01-01', count: 1, intensity: 1 }],
        years: [{ year: '2025' }],
      })

      const { rerender } = render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })

      currentTheme = 'dark'
      rerender(<UserDetailsPage />)

      await waitFor(() => {
        expect(drawContributions).toHaveBeenCalled()
        const firstArg = (drawContributions as jest.Mock).mock.calls[0][0]
        expect(firstArg).toBeInstanceOf(HTMLCanvasElement)
      })
    })

    test('calls drawContributions with correct data object', async () => {
      const mockData = {
        contributions: [{ date: '2025-01-01', count: 5, intensity: 2 }],
        years: [{ year: '2025' }],
      }
      ;(fetchHeatmapData as jest.Mock).mockResolvedValue(mockData)

      const { rerender } = render(<UserDetailsPage />)

      await waitFor(() => {
        expect(screen.getByAltText('Heatmap Background')).toBeInTheDocument()
      })

      currentTheme = 'dark'
      rerender(<UserDetailsPage />)

      await waitFor(() => {
        expect(drawContributions).toHaveBeenCalled()
        const callArgs = (drawContributions as jest.Mock).mock.calls[0][1]
        expect(callArgs.data).toBeDefined()
        expect(callArgs.username).toBe('test-user')
      })
    })
  })
})
