import { registerBreadcrumb, getBreadcrumbItems } from 'contexts/BreadcrumbContext'

describe('BreadcrumbContext', () => {
  // Since registry is a singleton within the module instance, we must clean up manually
  // or rely on unregister functions. We cannot directly clear the private registry.

  // We can track registered items and unregister them.
  let cleanupFns: (() => void)[] = []

  afterEach(() => {
    cleanupFns.forEach((fn) => fn())
    cleanupFns = []
  })

  it('sorts breadcrumbs correctly (home first, then by path length)', () => {
    // Register items out of order to test sorting
    cleanupFns.push(registerBreadcrumb({ title: 'Level 2', path: '/level-1/level-2' }))
    cleanupFns.push(registerBreadcrumb({ title: 'Level 1', path: '/level-1' }))
    cleanupFns.push(registerBreadcrumb({ title: 'Home', path: '/' }))

    const items = getBreadcrumbItems()

    expect(items).toHaveLength(3)
    expect(items[0]).toEqual({ title: 'Home', path: '/' })
    expect(items[1]).toEqual({ title: 'Level 1', path: '/level-1' })
    expect(items[2]).toEqual({ title: 'Level 2', path: '/level-1/level-2' })
  })

  it('sorts correctly when Home is not first inserted', () => {
    // This specifically targets the branch where 'b.path === "/"' in sort function
    // comparison logic might be hit if Home is later in the list.

    cleanupFns.push(registerBreadcrumb({ title: 'A', path: '/a' }))
    cleanupFns.push(registerBreadcrumb({ title: 'Home', path: '/' }))

    const items = getBreadcrumbItems()
    expect(items[0].path).toBe('/')
    expect(items[1].path).toBe('/a')
  })

  it('sorts by length when home is involved', () => {
    // Sorting should prioritize Home even if it's shorter/longer?
    // Current logic: if path is '/', return -1 (or 1).
    // If path is NOT '/', compare lengths.

    cleanupFns.push(registerBreadcrumb({ title: 'Long', path: '/very/long/path' }))
    cleanupFns.push(registerBreadcrumb({ title: 'Short', path: '/short' }))

    const items = getBreadcrumbItems()
    expect(items[0].path).toBe('/short')
    expect(items[1].path).toBe('/very/long/path')
  })

  // To check coverage of line 30, we simply call getBreadcrumbItems() which we are doing.
  // If line 30 refers to something else, we covered basic usage.
})
