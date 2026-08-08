import { act, renderHook } from '@testing-library/react'
import { useProfileSelection } from 'hooks/useProfileSelection'
import { createRef } from 'react'

type MockRangeInit = {
  text: string
  collapsed?: boolean
  rangeCount?: number
  rect?: Partial<DOMRect>
}

const setupSelection = ({
  text,
  collapsed = false,
  rangeCount = 1,
  rect = {},
  intersectsHighlight = false,
}: MockRangeInit & { intersectsHighlight?: boolean }) => {
  const startContainer = document.createElement('span')
  const endContainer = document.createElement('span')
  const boundingRect = { top: 20, left: 10, width: 100, height: 16, ...rect } as DOMRect
  const range = {
    startContainer,
    endContainer,
    getBoundingClientRect: () => boundingRect,
    intersectsNode: () => intersectsHighlight,
  }
  const selection = {
    rangeCount,
    isCollapsed: collapsed,
    getRangeAt: () => range,
    toString: () => text,
  }
  jest.spyOn(window, 'getSelection').mockReturnValue(selection as unknown as Selection)

  return { startContainer, endContainer, boundingRect }
}

describe('useProfileSelection', () => {
  afterEach(() => {
    jest.restoreAllMocks()
  })

  it('returns null when disabled', () => {
    const containerRef = createRef<HTMLDivElement>()
    const { result } = renderHook(() => useProfileSelection(containerRef, false))
    expect(result.current).toBeNull()
  })

  it('captures selection when both anchors are inside the container', () => {
    const container = document.createElement('div')
    document.body.appendChild(container)
    const { startContainer, endContainer, boundingRect } = setupSelection({
      text: '  hello world  ',
    })
    container.appendChild(startContainer)
    container.appendChild(endContainer)

    const containerRef = { current: container }
    const { result } = renderHook(() => useProfileSelection(containerRef, true))

    act(() => {
      document.dispatchEvent(new Event('selectionchange'))
    })

    expect(result.current).toEqual({ text: 'hello world', rect: boundingRect })
  })

  it('returns null when selection is outside the container', () => {
    const container = document.createElement('div')
    document.body.appendChild(container)
    setupSelection({ text: 'foo' })

    const containerRef = { current: container }
    const { result } = renderHook(() => useProfileSelection(containerRef, true))

    act(() => {
      document.dispatchEvent(new Event('selectionchange'))
    })

    expect(result.current).toBeNull()
  })

  it('returns null when selection has no range', () => {
    setupSelection({ text: '', rangeCount: 0 })
    const containerRef = { current: document.createElement('div') }
    const { result } = renderHook(() => useProfileSelection(containerRef, true))

    act(() => {
      document.dispatchEvent(new Event('selectionchange'))
    })

    expect(result.current).toBeNull()
  })

  it('returns null when selection is collapsed', () => {
    const container = document.createElement('div')
    const { startContainer, endContainer } = setupSelection({
      text: 'foo',
      collapsed: true,
    })
    container.appendChild(startContainer)
    container.appendChild(endContainer)

    const containerRef = { current: container }
    const { result } = renderHook(() => useProfileSelection(containerRef, true))

    act(() => {
      document.dispatchEvent(new Event('selectionchange'))
    })

    expect(result.current).toBeNull()
  })

  it('returns null when trimmed selection text is empty', () => {
    const container = document.createElement('div')
    const { startContainer, endContainer } = setupSelection({
      text: '   ',
    })
    container.appendChild(startContainer)
    container.appendChild(endContainer)

    const containerRef = { current: container }
    const { result } = renderHook(() => useProfileSelection(containerRef, true))

    act(() => {
      document.dispatchEvent(new Event('selectionchange'))
    })

    expect(result.current).toBeNull()
  })

  it('returns null when the selection intersects an existing claim highlight', () => {
    const container = document.createElement('div')
    document.body.appendChild(container)
    const highlight = document.createElement('span')
    highlight.setAttribute('data-claim-highlight', 'true')
    container.appendChild(highlight)
    const { startContainer, endContainer } = setupSelection({
      text: 'hello',
      intersectsHighlight: true,
    })
    container.appendChild(startContainer)
    container.appendChild(endContainer)

    const containerRef = { current: container }
    const { result } = renderHook(() => useProfileSelection(containerRef, true))

    act(() => {
      document.dispatchEvent(new Event('selectionchange'))
    })

    expect(result.current).toBeNull()
  })

  it('removes listener on unmount', () => {
    const removeSpy = jest.spyOn(document, 'removeEventListener')
    const containerRef = createRef<HTMLDivElement>()
    const { unmount } = renderHook(() => useProfileSelection(containerRef, true))
    unmount()
    expect(removeSpy).toHaveBeenCalledWith('selectionchange', expect.any(Function))
  })
})
