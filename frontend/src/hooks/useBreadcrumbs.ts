import { useBreadcrumb } from 'contexts/BreadcrumbContext'
import { usePathname } from 'next/navigation'
import type { BreadcrumbItem } from 'types/breadcrumb'
import { formatBreadcrumbTitle } from 'utils/breadcrumb'

export type { BreadcrumbItem } from 'types/breadcrumb'

const HIDDEN_SEGMENTS = new Set(['repositories', 'mentees', 'modules', 'programs', 'community'])
const COMMUNITY_RELATED_PATHS = ['/chapters', '/members', '/organizations']

function buildBreadcrumbItems(
  pathname: string | null,
  registeredItems: BreadcrumbItem[]
): BreadcrumbItem[] {
  const registeredMap = new Map<string, BreadcrumbItem>()
  for (const item of registeredItems || []) {
    registeredMap.set(item.path, item)
  }

  const items: BreadcrumbItem[] = [registeredMap.get('/') ?? { title: 'Home', path: '/' }]

  if (!pathname || pathname === '/') {
    return items
  }

  const segments = pathname.split('/').filter(Boolean)

  const shouldShowCommunity =
    pathname === '/community' ||
    pathname.startsWith('/community/') ||
    COMMUNITY_RELATED_PATHS.some((path) => pathname.startsWith(path))

  if (shouldShowCommunity) {
    items.push({
      title: 'Community',
      path: '/community',
    })
  }

  let currentPath = ''

  for (const segment of segments) {
    currentPath = `${currentPath}/${segment}`

    if (HIDDEN_SEGMENTS.has(segment)) continue

    const registeredItem = registeredMap.get(currentPath)
    if (registeredItem) {
      items.push(registeredItem)
    } else {
      items.push({
        title: formatBreadcrumbTitle(segment),
        path: currentPath,
      })
    }
  }

  return items
}

export function useBreadcrumbs(): BreadcrumbItem[] {
  const pathname = usePathname()
  const registeredItems = useBreadcrumb()

  return buildBreadcrumbItems(pathname, registeredItems)
}
