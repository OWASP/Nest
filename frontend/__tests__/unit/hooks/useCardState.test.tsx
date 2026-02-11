import { renderHook, act } from '@testing-library/react'
import { useCardState } from 'hooks/useCardState'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value
    }),
    removeItem: jest.fn((key) => {
      delete store[key]
    }),
    clear: jest.fn(() => {
      store = {}
    }),
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('useCardState', () => {
  beforeEach(() => {
    localStorageMock.clear()
    jest.clearAllMocks()
  })

  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useCardState('test-card'))
    
    expect(result.current.isCardActive('test-card')).toBe(false)
    expect(result.current.isCardVisited('test-card')).toBe(false)
    expect(result.current.cardState.isActive).toBe(false)
    expect(result.current.cardState.isVisited).toBe(false)
  })

  it('should mark card as active and visited when clicked', () => {
    const { result } = renderHook(() => useCardState('test-card'))
    
    act(() => {
      result.current.handleCardClick('test-card')
    })
    
    expect(result.current.isCardActive('test-card')).toBe(true)
    expect(result.current.isCardVisited('test-card')).toBe(true)
  })

  it('should remove active state after timeout', async () => {
    const { result } = renderHook(() => useCardState('test-card'))
    
    act(() => {
      result.current.handleCardClick('test-card')
    })
    
    expect(result.current.isCardActive('test-card')).toBe(true)
    
    // Wait for timeout (150ms)
    await new Promise(resolve => setTimeout(resolve, 200))
    
    expect(result.current.isCardActive('test-card')).toBe(false)
    expect(result.current.isCardVisited('test-card')).toBe(true)
  })

  it('should load visited cards from localStorage on mount', () => {
    localStorageMock.setItem('nest-visited-cards', JSON.stringify(['visited-card']))
    
    const { result } = renderHook(() => useCardState('visited-card'))
    
    expect(result.current.isCardVisited('visited-card')).toBe(true)
    expect(result.current.isCardActive('visited-card')).toBe(false)
  })

  it('should save visited cards to localStorage', () => {
    const { result } = renderHook(() => useCardState('test-card'))
    
    act(() => {
      result.current.handleCardClick('test-card')
    })
    
    // Wait for timeout and localStorage save
    setTimeout(() => {
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'nest-visited-cards',
        JSON.stringify(['test-card'])
      )
    }, 200)
  })

  it('should handle multiple cards independently', () => {
    const { result: result1 } = renderHook(() => useCardState('card-1'))
    const { result: result2 } = renderHook(() => useCardState('card-2'))
    
    act(() => {
      result1.current.handleCardClick('card-1')
    })
    
    expect(result1.current.isCardVisited('card-1')).toBe(true)
    expect(result1.current.isCardVisited('card-2')).toBe(false)
    expect(result2.current.isCardVisited('card-1')).toBe(true)
    expect(result2.current.isCardVisited('card-2')).toBe(false)
  })

  it('should handle localStorage errors gracefully', () => {
    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation()
    localStorageMock.setItem.mockImplementation(() => {
      throw new Error('Storage error')
    })
    
    const { result } = renderHook(() => useCardState('test-card'))
    
    act(() => {
      result.current.handleCardClick('test-card')
    })
    
    setTimeout(() => {
      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to save visited cards to localStorage:',
        expect.any(Error)
      )
    }, 200)
    
    consoleSpy.mockRestore()
  })
})
