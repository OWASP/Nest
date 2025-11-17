import { library } from '@fortawesome/fontawesome-svg-core'
import { faLink } from '@fortawesome/free-solid-svg-icons'
import { screen, render, fireEvent, waitFor } from '@testing-library/react'
import slugifyMock from 'utils/slugify'
import AnchorTitle from 'components/AnchorTitle'

library.add(faLink)

jest.mock('utils/slugify', () => ({
  __esModule: true,
  default: jest.fn((str: string) =>
    str
      .toLowerCase()
      .replaceAll(/[^a-z0-9]/g, '-')
      .replaceAll(/-{2,10}/g, '-')
      .replaceAll(/(^-{1,10}|-{1,10}$)/g, '')
  ),
}))

// Helper functions to reduce nesting
const createMockBoundingClientRect = () => ({
  top: 100,
  height: 50,
  width: 200,
  bottom: 150,
  left: 0,
  right: 200,
  x: 0,
  y: 100,
  toJSON: () => {},
})

const createMockElement = (getBoundingClientRect: jest.SpyInstance | jest.Mock) => ({
  getBoundingClientRect,
  querySelector: jest.fn(() => ({
    offsetHeight: 30,
  })),
})

const setupMockAnimationFrame = (cb: (time: number) => void) => {
  cb(0)
  return 0
}

const createMockElementForUseEffect = () => ({
  getBoundingClientRect: jest.fn(() => createMockBoundingClientRect()),
  querySelector: jest.fn(() => ({
    offsetHeight: 30,
  })),
})

const setupAnimationFrameForUseEffect = (cb: (time: number) => void) => {
  cb(0)
  return 0
}

const createMockElementWithNullQuery = () => ({
  getBoundingClientRect: jest.fn(() => createMockBoundingClientRect()),
  querySelector: jest.fn(() => null),
})

const createMockElementForOffset = () => ({
  getBoundingClientRect: jest.fn(() => ({ top: 100 })),
  querySelector: jest.fn(() => ({ offsetHeight: 30 })),
})

const setupAnimationFrameForHash = (cb: (time: number) => void) => {
  cb(0)
  return 0
}

describe('AnchorTitle Component', () => {
  afterEach(() => {
    jest.restoreAllMocks()
    globalThis.history.replaceState(null, '', globalThis.location.pathname)
  })

  describe('Basic Rendering', () => {
    it('renders without crashing', () => {
      render(<AnchorTitle title="Test Title" />)
      expect(screen.getByText('Test Title')).toBeInTheDocument()
    })

    it('displays the correct title text', () => {
      const testTitle = 'Sample Heading'
      render(<AnchorTitle title={testTitle} />)
      expect(screen.getByText(testTitle)).toBeInTheDocument()
    })

    it('renders with correct HTML structure', () => {
      render(<AnchorTitle title="Test" />)

      const container = screen.getByText('Test').closest('div')
      expect(container).toHaveClass('flex', 'items-center', 'text-2xl', 'font-semibold')

      const groupContainer = screen.getByText('Test').closest('.group')
      expect(groupContainer).toHaveClass('group', 'relative', 'flex', 'items-center')

      const titleElement = screen.getByText('Test')
      expect(titleElement).toHaveClass('flex', 'items-center', 'text-2xl', 'font-semibold')
      expect(titleElement).toHaveAttribute('data-anchor-title', 'true')
    })

    it('renders FontAwesome link icon', () => {
      render(<AnchorTitle title="Test" />)
      const link = screen.getByRole('link')
      const icon = link.querySelector('svg')
      expect(icon).toBeInTheDocument()
      expect(link).toHaveClass(
        'inherit-color',
        'ml-2',
        'opacity-0',
        'transition-opacity',
        'duration-200',
        'group-hover:opacity-100'
      )
    })
  })

  describe('Prop-Based Behaviour', () => {
    it('generates correct ID and href from title using slugify', () => {
      const testTitle = 'Test title with spaces'
      render(<AnchorTitle title={testTitle} />)

      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '#test-title-with-spaces')

      const element = document.getElementById('test-title-with-spaces')
      expect(element).toBeInTheDocument()
    })

    it('handles different title formats correctly', () => {
      const titles = [
        'Simple Title',
        'Test with Numbers 123',
        'Title-with-hyphens',
        'Title_with_underscores',
      ]

      const titleRegex = /^#[a-z0-9-]+$/

      for (const title of titles) {
        const { unmount } = render(<AnchorTitle title={title} />)
        const link = screen.getByRole('link')
        const href = link.getAttribute('href')
        expect(href).toMatch(titleRegex)
        unmount()
      }
    })
  })

  describe('Event Handling', () => {
    let mockScrollTo: jest.SpyInstance
    let mockPushState: jest.SpyInstance
    let mockGetBoundingClientRect: jest.SpyInstance
    let mockGetElementById: jest.SpyInstance
    let mockRequestAnimationFrame: jest.SpyInstance

    const setupMocks = () => {
      mockScrollTo = jest.spyOn(globalThis, 'scrollTo').mockImplementation()
      mockPushState = jest.spyOn(globalThis.history, 'pushState').mockImplementation()
      mockRequestAnimationFrame = jest
        .spyOn(globalThis, 'requestAnimationFrame')
        .mockImplementation(setupMockAnimationFrame)

      mockGetBoundingClientRect = jest.fn(createMockBoundingClientRect)
      const mockElement = createMockElement(mockGetBoundingClientRect)
      mockGetElementById = jest
        .spyOn(document, 'getElementById')
        .mockReturnValue(mockElement as unknown as HTMLElement)
    }

    const cleanupMocks = () => {
      mockScrollTo.mockRestore()
      mockPushState.mockRestore()
      mockRequestAnimationFrame.mockRestore()
      mockGetElementById.mockRestore()
    }

    beforeEach(setupMocks)
    afterEach(cleanupMocks)

    it('prevents default behaviour on link click', () => {
      render(<AnchorTitle title="Click Test" />)
      const link = screen.getByRole('link')

      const mockPreventDefault = jest.fn()
      const clickEvent = new MouseEvent('click', { bubbles: true })
      Object.defineProperty(clickEvent, 'preventDefault', { value: mockPreventDefault })

      fireEvent(link, clickEvent)
      expect(mockPreventDefault).toHaveBeenCalled()
    })

    it('calls scrollTo with correct parameters on click', () => {
      render(<AnchorTitle title="Scroll Test" />)
      const link = screen.getByRole('link')

      fireEvent.click(link)

      expect(mockScrollTo).toHaveBeenCalledWith({
        behavior: 'smooth',
        top: 20,
      })
    })

    it('updates browser history on click', () => {
      render(<AnchorTitle title="History Test" />)
      const link = screen.getByRole('link')

      fireEvent.click(link)

      expect(mockPushState).toHaveBeenCalledWith(null, '', '#history-test')
    })

    it('calculates scroll position correctly with heading offset', () => {
      render(<AnchorTitle title="Offset Test" />)
      const link = screen.getByRole('link')

      fireEvent.click(link)

      expect(mockScrollTo).toHaveBeenCalledWith({
        top: 20,
        behavior: 'smooth',
      })
    })
  })

  describe('useEffect Behaviour', () => {
    let mockScrollTo: jest.SpyInstance
    let mockGetElementById: jest.SpyInstance
    let mockRequestAnimationFrame: jest.SpyInstance

    const setupUseEffectMocks = () => {
      mockScrollTo = jest.spyOn(globalThis, 'scrollTo').mockImplementation()
      mockRequestAnimationFrame = jest
        .spyOn(globalThis, 'requestAnimationFrame')
        .mockImplementation(setupAnimationFrameForUseEffect)

      const mockElement = createMockElementForUseEffect()
      mockGetElementById = jest
        .spyOn(document, 'getElementById')
        .mockReturnValue(mockElement as unknown as HTMLElement)
    }

    const cleanupUseEffectMocks = () => {
      mockScrollTo.mockRestore()
      mockRequestAnimationFrame.mockRestore()
      mockGetElementById.mockRestore()
    }

    beforeEach(setupUseEffectMocks)
    afterEach(cleanupUseEffectMocks)

    it('scrolls to element on mount when hash matches', async () => {
      globalThis.location.hash = '#test-scroll'

      render(<AnchorTitle title="Test Scroll" />)

      await waitFor(() => {
        expect(mockRequestAnimationFrame).toHaveBeenCalled()
        expect(mockScrollTo).toHaveBeenCalledWith({
          top: 20,
          behavior: 'smooth',
        })
      })
    })

    it('does not scroll when hash does not match', () => {
      globalThis.location.hash = '#different-hash'

      render(<AnchorTitle title="Test Scroll" />)

      expect(mockScrollTo).not.toHaveBeenCalled()
    })
    it('handles popstate events correctly', async () => {
      render(<AnchorTitle title="Popstate Test" />)

      globalThis.location.hash = '#popstate-test'

      const popstateEvent = new PopStateEvent('popstate')
      fireEvent(globalThis as unknown as Window, popstateEvent)

      await waitFor(() => {
        expect(mockRequestAnimationFrame).toHaveBeenCalled()
        expect(mockScrollTo).toHaveBeenCalled()
      })
    })

    it('removes popstate event listener on unmount', () => {
      const mockRemoveEventListener = jest.spyOn(globalThis, 'removeEventListener')

      const { unmount } = render(<AnchorTitle title="Cleanup Test" />)
      unmount()

      expect(mockRemoveEventListener).toHaveBeenCalledWith('popstate', expect.any(Function))
    })
  })

  describe('Edge Cases and Error Handling', () => {
    it('handles empty title gracefully', () => {
      render(<AnchorTitle title="" />)

      const container = document.querySelector('div[id=""]')
      expect(container).toBeInTheDocument()

      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '#')
    })

    it('handles special character in title', () => {
      const specialTitle = 'Title with @#$%^&*()'
      render(<AnchorTitle title={specialTitle} />)

      expect(screen.getByText(specialTitle)).toBeInTheDocument()
      const link = screen.getByRole('link')
      const specialCharRegex = /^#[a-z0-9-]*$/
      const href = link.getAttribute('href')
      expect(href).toMatch(specialCharRegex)
    })

    it('handles very long titles', () => {
      const longTitle =
        'This is a very long title that might cause issues with ID generation and should be handled gracefully by the component'
      render(<AnchorTitle title={longTitle} />)

      expect(screen.getByText(longTitle)).toBeInTheDocument()
      const link = screen.getByRole('link')
      expect(link.getAttribute('href')).toBeDefined()
    })

    it('handles missing DOM element gracefully', () => {
      const mockGetElementById = jest.spyOn(document, 'getElementById').mockReturnValue(null)
      const mockConsoleError = jest.spyOn(console, 'error').mockImplementation(() => {})

      render(<AnchorTitle title="Missing Element" />)
      const link = screen.getByRole('link')

      expect(() => fireEvent.click(link)).not.toThrow()

      mockGetElementById.mockRestore()
      mockConsoleError.mockRestore()
    })

    it('handles missing anchor-title element in scroll calculation', () => {
      const mockElement = createMockElementWithNullQuery()
      const mockGetElementById = jest
        .spyOn(document, 'getElementById')
        .mockReturnValue(mockElement as unknown as HTMLElement)
      const mockScrollTo = jest.spyOn(globalThis, 'scrollTo').mockImplementation()

      render(<AnchorTitle title="No Anchor" />)
      const link = screen.getByRole('link')

      expect(() => fireEvent.click(link)).not.toThrow()

      mockGetElementById.mockRestore()
      mockScrollTo.mockRestore()
    })
  })

  describe('Accessibility', () => {
    it('has proper link role and attributes', () => {
      render(<AnchorTitle title="Accessibility Test" />)

      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '#accessibility-test')
      expect(link).toBeInTheDocument()
    })

    it('provides proper heading structure', () => {
      render(<AnchorTitle title="Heading Test" />)

      const titleElement = screen.getByText('Heading Test')
      expect(titleElement).toHaveAttribute('data-anchor-title', 'true')
      expect(titleElement).toHaveClass('text-2xl', 'font-semibold')

      const container = document.getElementById('heading-test')
      expect(container).toHaveAttribute('id', 'heading-test')
      expect(container).toBeInTheDocument()
    })

    it('maintains focus management on interaction', () => {
      const mockScrollTo = jest.spyOn(globalThis, 'scrollTo').mockImplementation()
      const mockPushState = jest.spyOn(globalThis.history, 'pushState').mockImplementation()

      render(<AnchorTitle title="Focus Test" />)

      const link = screen.getByRole('link')
      link.focus()
      expect(document.activeElement).toBe(link)

      fireEvent.click(link)

      expect(document.activeElement).toBeDefined()

      mockScrollTo.mockRestore()
      mockPushState.mockRestore()
    })
  })

  describe('Integration Tests', () => {
    it('works correctly with multiple instances', () => {
      render(
        <div>
          <AnchorTitle title="First Title" />
          <AnchorTitle title="Second Title" />
        </div>
      )

      expect(screen.getByText('First Title')).toBeInTheDocument()
      expect(screen.getByText('Second Title')).toBeInTheDocument()

      const links = screen.getAllByRole('link')
      expect(links).toHaveLength(2)
      expect(links[0]).toHaveAttribute('href', '#first-title')
      expect(links[1]).toHaveAttribute('href', '#second-title')
    })

    it('handles rapid successive clicks', () => {
      const mockScrollTo = jest.spyOn(globalThis, 'scrollTo').mockImplementation()
      const mockPushState = jest.spyOn(globalThis.history, 'pushState').mockImplementation()

      render(<AnchorTitle title="Rapid Click" />)
      const link = screen.getByRole('link')

      fireEvent.click(link)
      fireEvent.click(link)
      fireEvent.click(link)

      expect(mockScrollTo).toHaveBeenCalledTimes(3)
      expect(mockPushState).toHaveBeenCalledTimes(3)

      mockScrollTo.mockRestore()
      mockPushState.mockRestore()
    })

    it('updates correctly when title prop changes', () => {
      const { rerender } = render(<AnchorTitle title="Original Title" />)
      expect(screen.getByText('Original Title')).toBeInTheDocument()

      rerender(<AnchorTitle title="Updated Title" />)
      expect(screen.getByText('Updated Title')).toBeInTheDocument()
      expect(screen.queryByText('Original Title')).not.toBeInTheDocument()

      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '#updated-title')
    })
  })

  describe('Browser API Interactions', () => {
    it('handles window.pageYOffset correctly', () => {
      const mockScrollTo = jest.spyOn(globalThis, 'scrollTo').mockImplementation()
      const originalPageYOffset = window.pageYOffset

      Object.defineProperty(globalThis, 'pageYOffset', {
        value: 500,
        configurable: true,
      })

      const mockElement = createMockElementForOffset()
      const mockGetElementById = jest
        .spyOn(document, 'getElementById')
        .mockReturnValue(mockElement as unknown as HTMLElement)

      render(<AnchorTitle title="Offset Test" />)
      const link = screen.getByRole('link')

      fireEvent.click(link)

      expect(mockScrollTo).toHaveBeenCalledWith({
        top: 20,
        behavior: 'smooth',
      })

      Object.defineProperty(globalThis, 'pageYOffset', {
        value: originalPageYOffset,
        configurable: true,
      })

      mockScrollTo.mockRestore()
      mockGetElementById.mockRestore()
    })

    it('handles hash changes in the URL correctly', async () => {
      const mockScrollTo = jest.spyOn(globalThis, 'scrollTo').mockImplementation()
      const mockRequestAnimationFrame = jest
        .spyOn(globalThis, 'requestAnimationFrame')
        .mockImplementation(setupAnimationFrameForHash)

      globalThis.location.hash = ''
      render(<AnchorTitle title="Hash Test" />)

      globalThis.location.hash = '#hash-test'
      const popstateEvent = new PopStateEvent('popstate')
      fireEvent(globalThis as unknown as Window, popstateEvent)

      await waitFor(() => {
        expect(mockScrollTo).toHaveBeenCalled()
      })

      mockScrollTo.mockRestore()
      mockRequestAnimationFrame.mockRestore()
    })
  })

  describe('Performance and Optimization', () => {
    it('uses useCallback for scrollToElement function', () => {
      const mockScrollTo = jest.spyOn(globalThis, 'scrollTo').mockImplementation()

      const { rerender } = render(<AnchorTitle title="Callback Test" />)
      const link1 = screen.getByRole('link')

      fireEvent.click(link1)

      rerender(<AnchorTitle title="Callback Test" />)
      const link2 = screen.getByRole('link')

      fireEvent.click(link2)

      expect(mockScrollTo).toHaveBeenCalledTimes(2)
      mockScrollTo.mockRestore()
    })

    it('cleans up event listeners properly', () => {
      const mockAddEventListener = jest.spyOn(globalThis, 'addEventListener')
      const mockRemoveEventListener = jest.spyOn(globalThis, 'removeEventListener')

      const { unmount } = render(<AnchorTitle title="Cleanup Test" />)

      expect(mockAddEventListener).toHaveBeenCalledWith('popstate', expect.any(Function))

      unmount()

      expect(mockRemoveEventListener).toHaveBeenCalledWith('popstate', expect.any(Function))

      mockAddEventListener.mockRestore()
      mockRemoveEventListener.mockRestore()
    })
  })

  describe('State Changes and Internal Logic', () => {
    it('recalculates scroll position when element dimensions change', () => {
      const mockScrollTo = jest.spyOn(globalThis, 'scrollTo').mockImplementation()

      const offsetHeights = { current: 30 }
      const mockElement = {
        getBoundingClientRect: jest.fn(() => ({ top: 100 })),
        querySelector: jest.fn(() => ({ offsetHeight: offsetHeights.current })),
      }
      const mockGetElementById = jest
        .spyOn(document, 'getElementById')
        .mockReturnValue(mockElement as unknown as HTMLElement)

      render(<AnchorTitle title="Dynamic Height" />)
      const link = screen.getByRole('link')

      fireEvent.click(link)
      const firstCall = (mockScrollTo.mock.calls[0][0] as unknown as { top: number }).top

      offsetHeights.current = 60
      fireEvent.click(link)
      const secondCall = (mockScrollTo.mock.calls[1][0] as unknown as { top: number }).top

      expect(firstCall).toBe(secondCall)
      expect(Math.abs(firstCall - secondCall)).toBe(0)

      mockScrollTo.mockRestore()
      mockGetElementById.mockRestore()
    })

    it('handles component rerender with different IDs', () => {
      const mockAddEventListener = jest.spyOn(globalThis, 'addEventListener')
      const mockRemoveEventListener = jest.spyOn(globalThis, 'removeEventListener')

      const { rerender } = render(<AnchorTitle title="Original" />)
      const originalAddCalls = mockAddEventListener.mock.calls.length

      rerender(<AnchorTitle title="Changed" />)

      expect(mockRemoveEventListener).toHaveBeenCalled()
      expect(mockAddEventListener.mock.calls.length).toBeGreaterThan(originalAddCalls)

      mockAddEventListener.mockRestore()
      mockRemoveEventListener.mockRestore()
    })
  })

  describe('CSS and Styling', () => {
    it('applies correct CSS classes for visual behaviour', () => {
      render(<AnchorTitle title="Style Test" />)

      const link = screen.getByRole('link')
      expect(link).toHaveClass(
        'inherit-color',
        'ml-2',
        'opacity-0',
        'transition-opacity',
        'duration-200',
        'group-hover:opacity-100'
      )
    })

    it('has correct icon styling', () => {
      render(<AnchorTitle title="Icon Test" />)

      const icon = screen.getByRole('link').querySelector('svg')
      expect(icon).toBeInTheDocument()
      expect(icon).toHaveClass('custom-icon', 'h-7', 'w-5')
    })

    it('maintains proper layout structure', () => {
      render(<AnchorTitle title="Layout Test" />)

      const titleContainer = screen.getByText('Layout Test').closest('div')
      expect(titleContainer).toHaveClass('flex', 'items-center', 'text-2xl', 'font-semibold')

      const groupContainer = titleContainer?.closest('.group')
      expect(groupContainer).toHaveClass('group', 'relative', 'flex', 'items-center')
    })
  })

  describe('Dependencies and Mocking', () => {
    it('uses slugify utility correctly', () => {
      render(<AnchorTitle title="Slugify Test" />)
      expect(slugifyMock).toHaveBeenCalledWith('Slugify Test')
    })

    it('handles slugify returning different formats', () => {
      const mockFn = slugifyMock as jest.MockedFunction<typeof slugifyMock>
      const originalImplementation = mockFn.getMockImplementation()
      mockFn.mockReturnValue('custom-slug-format')

      render(<AnchorTitle title="Custom Slug" />)

      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '#custom-slug-format')

      const element = document.getElementById('custom-slug-format')
      expect(element).toBeInTheDocument()

      if (originalImplementation) {
        mockFn.mockImplementation(originalImplementation)
      }
    })
  })

  describe('Comprehensive User Interactions', () => {
    it('complete user journey: render → hover → click → navigate', () => {
      const mockFn = slugifyMock as jest.MockedFunction<typeof slugifyMock>

      mockFn.mockImplementation((str: string) =>
        str
          .toLowerCase()
          .replaceAll(/[^a-z0-9]/g, '-')
          .replaceAll(/-{2,10}/g, '-')
          .replaceAll(/(^-{1,10}|-{1,10}$)/g, '')
      )

      const mockScrollTo = jest.spyOn(globalThis, 'scrollTo').mockImplementation()
      const mockPushState = jest.spyOn(globalThis.history, 'pushState').mockImplementation()

      render(<AnchorTitle title="User Journey" />)

      const titleElement = screen.getByText('User Journey')
      expect(titleElement).toBeInTheDocument()

      const link = screen.getByRole('link')
      expect(link).toHaveClass('opacity-0')

      fireEvent.click(link)

      expect(mockScrollTo).toHaveBeenCalledWith({
        top: expect.any(Number),
        behavior: 'smooth',
      })
      expect(mockPushState).toHaveBeenCalledWith(null, '', '#user-journey')

      mockScrollTo.mockRestore()
      mockPushState.mockRestore()
    })

    it('handles keyboard navigation', () => {
      render(<AnchorTitle title="Keyboard Test" />)

      const link = screen.getByRole('link')

      link.focus()
      expect(document.activeElement).toBe(link)

      fireEvent.keyDown(link, { key: 'Enter', code: 'Enter' })
    })
  })
})
