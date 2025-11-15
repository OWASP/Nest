import { renderHook } from '@testing-library/react'
import { useBreadcrumbs } from 'hooks/useBreadcrumbs'
import { usePathname } from 'next/navigation'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

describe('useBreadcrumbs', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Single-slug routes', () => {
    test('generates breadcrumbs for project page with projectName', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

      const { result } = renderHook(() => useBreadcrumbs({ projectName: 'OWASP ZAP' }))

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Projects', path: '/projects' },
        { title: 'OWASP ZAP', path: '/projects/zap' },
      ])
    })

    test('fallback to formatted slug if projectName not provided', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/juice-shop')

      const { result } = renderHook(() => useBreadcrumbs({}))

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Projects', path: '/projects' },
        { title: 'Juice shop', path: '/projects/juice-shop' },
      ])
    })

    test('generates breadcrumbs for member page with memberName', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/members/bjornkimminich')

      const { result } = renderHook(() => useBreadcrumbs({ memberName: 'Björn Kimminich' }))

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Members', path: '/members' },
        { title: 'Björn Kimminich', path: '/members/bjornkimminich' },
      ])
    })

    test('generates breadcrumbs for chapter page with chapterName', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/chapters/bangalore')

      const { result } = renderHook(() => useBreadcrumbs({ chapterName: 'Bangalore Chapter' }))

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Chapters', path: '/chapters' },
        { title: 'Bangalore Chapter', path: '/chapters/bangalore' },
      ])
    })

    test('generates breadcrumbs for committee page with committeeName', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/committees/outreach')

      const { result } = renderHook(() => useBreadcrumbs({ committeeName: 'Outreach Committee' }))

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Committees', path: '/committees' },
        { title: 'Outreach Committee', path: '/committees/outreach' },
      ])
    })

    test('generates breadcrumbs for organization page with orgName', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/organizations/cyclonedx')

      const { result } = renderHook(() => useBreadcrumbs({ orgName: 'CycloneDX BOM Standard' }))

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Organizations', path: '/organizations' },
        { title: 'CycloneDX BOM Standard', path: '/organizations/cyclonedx' },
      ])
    })
  })

  describe('Multi-slug routes (nested repositories)', () => {
    test('detects nested repository route pattern', () => {
      ;(usePathname as jest.Mock).mockReturnValue(
        '/organizations/cyclonedx/repositories/cyclonedx-python'
      )

      const { result } = renderHook(() =>
        useBreadcrumbs({
          orgName: 'CycloneDX BOM Standard',
          repoName: 'Cyclonedx Python',
        })
      )

      expect(result.current).toHaveLength(4)
    })

    test('generates correct breadcrumbs for repository page', () => {
      ;(usePathname as jest.Mock).mockReturnValue(
        '/organizations/cyclonedx/repositories/cyclonedx-python'
      )

      const { result } = renderHook(() =>
        useBreadcrumbs({
          orgName: 'CycloneDX BOM Standard',
          repoName: 'Cyclonedx Python',
        })
      )

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Organizations', path: '/organizations' },
        {
          title: 'CycloneDX BOM Standard',
          path: '/organizations/cyclonedx',
        },
        {
          title: 'Cyclonedx Python',
          path: '/organizations/cyclonedx/repositories/cyclonedx-python',
        },
      ])
    })

    test('uses orgName from breadcrumbData', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/organizations/owasp-amass/repositories/amass')

      const { result } = renderHook(() =>
        useBreadcrumbs({
          orgName: 'OWASP Amass Project',
          repoName: 'Amass',
        })
      )

      const orgBreadcrumb = result.current.find(
        (item) => item.path === '/organizations/owasp-amass'
      )
      expect(orgBreadcrumb?.title).toBe('OWASP Amass Project')
    })

    test('formats repo name by splitting dashes and capitalizing', () => {
      ;(usePathname as jest.Mock).mockReturnValue(
        '/organizations/cyclonedx/repositories/cyclonedx-maven-plugin'
      )

      const { result } = renderHook(() => useBreadcrumbs({}))

      const repoBreadcrumb = result.current[result.current.length - 1]
      expect(repoBreadcrumb.title).toBe('Cyclonedx maven plugin')
    })

    test('fallback to formatted slugs if data not provided', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/organizations/some-org/repositories/some-repo')

      const { result } = renderHook(() => useBreadcrumbs({}))

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Organizations', path: '/organizations' },
        { title: 'Some org', path: '/organizations/some-org' },
        {
          title: 'Some repo',
          path: '/organizations/some-org/repositories/some-repo',
        },
      ])
    })
  })

  describe('Path building', () => {
    test('builds progressive paths correctly', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

      const { result } = renderHook(() => useBreadcrumbs({ projectName: 'OWASP ZAP' }))

      expect(result.current[0].path).toBe('/')
      expect(result.current[1].path).toBe('/projects')
      expect(result.current[2].path).toBe('/projects/zap')
    })

    test('builds correct nested paths for repos', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/organizations/org/repositories/repo')

      const { result } = renderHook(() =>
        useBreadcrumbs({ orgName: 'Org Name', repoName: 'Repo Name' })
      )

      expect(result.current[0].path).toBe('/')
      expect(result.current[1].path).toBe('/organizations')
      expect(result.current[2].path).toBe('/organizations/org')
      expect(result.current[3].path).toBe('/organizations/org/repositories/repo')
    })
  })

  describe('Edge cases', () => {
    test('handles undefined breadcrumbData', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/test')

      const { result } = renderHook(() => useBreadcrumbs(undefined))

      expect(result.current).toEqual([
        { title: 'Home', path: '/' },
        { title: 'Projects', path: '/projects' },
        { title: 'Test', path: '/projects/test' },
      ])
    })

    test('handles partial breadcrumbData (uses first matching field)', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

      const { result } = renderHook(() => useBreadcrumbs({ memberName: 'John Doe' }))

      expect(result.current[2].title).toBe('John Doe')
    })

    test('handles paths with trailing slashes', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap/')

      const { result } = renderHook(() => useBreadcrumbs({ projectName: 'OWASP ZAP' }))

      expect(result.current).toHaveLength(3)
      expect(result.current[2].title).toBe('OWASP ZAP')
    })

    test('each breadcrumb item has title and path properties', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

      const { result } = renderHook(() => useBreadcrumbs({ projectName: 'OWASP ZAP' }))

      result.current.forEach((item) => {
        expect(item).toHaveProperty('title')
        expect(item).toHaveProperty('path')
        expect(typeof item.title).toBe('string')
        expect(typeof item.path).toBe('string')
      })
    })
  })
})
