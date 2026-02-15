import { registerBreadcrumb, getBreadcrumbItems } from 'contexts/BreadcrumbContext'

describe('BreadcrumbContext', () => {
  let cleanupFns: (() => void)[] = []

  afterEach(() => {
    cleanupFns.forEach((fn) => {
      fn()
    })
    cleanupFns = []
  })

  it('sorts breadcrumbs correctly (home first, then by path length)', () => {
    cleanupFns.push(
      registerBreadcrumb({ title: 'Level 2', path: '/level-1/level-2' }),
      registerBreadcrumb({ title: 'Level 1', path: '/level-1' }),
      registerBreadcrumb({ title: 'Home', path: '/' })
    )

    const items = getBreadcrumbItems()

    expect(items).toHaveLength(3)
    expect(items[0]).toEqual({ title: 'Home', path: '/' })
    expect(items[1]).toEqual({ title: 'Level 1', path: '/level-1' })
    expect(items[2]).toEqual({ title: 'Level 2', path: '/level-1/level-2' })
  })

  it('sorts correctly when Home is not first inserted', () => {
    cleanupFns.push(
      registerBreadcrumb({ title: 'A', path: '/a' }),
      registerBreadcrumb({ title: 'Home', path: '/' })
    )

    const items = getBreadcrumbItems()
    expect(items[0].path).toBe('/')
    expect(items[1].path).toBe('/a')
  })

  it('sorts by path length when home is not present', () => {
    cleanupFns.push(
      registerBreadcrumb({ title: 'Long', path: '/very/long/path' }),
      registerBreadcrumb({ title: 'Short', path: '/short' })
    )

    const items = getBreadcrumbItems()
    expect(items[0].path).toBe('/short')
    expect(items[1].path).toBe('/very/long/path')
  })
})
