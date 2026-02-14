import { renderHook, act } from '@testing-library/react'
import { BreadcrumbRoot, registerBreadcrumb } from 'contexts/BreadcrumbContext'
import { useBreadcrumbs } from 'hooks/useBreadcrumbs'
import { usePathname } from 'next/navigation'
import React from 'react'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

// Helper wrapper with BreadcrumbRoot
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BreadcrumbRoot>{children}</BreadcrumbRoot>
)

describe('useBreadcrumbs', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Hybrid Pattern (registered + auto-generated)', () => {
    test('returns Home for root path', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/')

      const { result } = renderHook(() => useBreadcrumbs(), { wrapper })

      expect(result.current).toEqual([{ title: 'Home', path: '/' }])
    })

    test('auto-generates breadcrumbs from URL when no items registered', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/members')

      const { result } = renderHook(() => useBreadcrumbs(), { wrapper })

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Community', path: '/community' },
        { title: 'Members', path: '/members' },
      ])
    })

    test('uses registered title when available', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/test-project')

      const { result } = renderHook(() => useBreadcrumbs(), { wrapper })

      let unregister: () => void
      act(() => {
        unregister = registerBreadcrumb({ title: 'Test Project', path: '/projects/test-project' })
      })

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Projects', path: '/projects' },
        { title: 'Test Project', path: '/projects/test-project' },
      ])

      act(() => {
        unregister()
      })
    })

    test('merges registered and auto-generated items', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/organizations/test-org/repositories/test-repo')

      const { result } = renderHook(() => useBreadcrumbs(), { wrapper })

      const unregisterFns: (() => void)[] = []
      act(() => {
        unregisterFns.push(
          registerBreadcrumb({ title: 'Test Organization', path: '/organizations/test-org' }),
          registerBreadcrumb({
            title: 'Test Repository',
            path: '/organizations/test-org/repositories/test-repo',
          })
        )
      })

      // Note: 'repositories' segment is hidden (in HIDDEN_SEGMENTS)
      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Community', path: '/community' },
        { title: 'Organizations', path: '/organizations' },
        { title: 'Test Organization', path: '/organizations/test-org' },
        { title: 'Test Repository', path: '/organizations/test-org/repositories/test-repo' },
      ])

      act(() => {
        for (const fn of unregisterFns) {
          fn()
        }
      })
    })
  })

  describe('HIDDEN_SEGMENTS', () => {
    test('does not show "community" in breadcrumbs when present in path', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/community/forum')

      const { result } = renderHook(() => useBreadcrumbs(), { wrapper })

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Community', path: '/community' },
        { title: 'Forum', path: '/community/forum' },
      ])
    })
    test('hides multiple HIDDEN_SEGMENTS in the same path', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/community/mentees/profile')

      const { result } = renderHook(() => useBreadcrumbs(), { wrapper })

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Community', path: '/community' },
        { title: 'Profile', path: '/community/mentees/profile' },
      ])
    })
  })

  describe('Edge cases', () => {
    test('handles null pathname', () => {
      ;(usePathname as jest.Mock).mockReturnValue(null)

      const { result } = renderHook(() => useBreadcrumbs(), { wrapper })

      expect(result.current).toEqual([{ title: 'Home', path: '/' }])
    })

    test('formats hyphenated URL segments', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/test-page/test-section')

      const { result } = renderHook(() => useBreadcrumbs(), { wrapper })

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Test Page', path: '/test-page' },
        { title: 'Test Section', path: '/test-page/test-section' },
      ])
    })
  })
})
