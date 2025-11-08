import upperFirst from 'lodash/upperFirst'
import { usePathname } from 'next/navigation'

export interface BreadCrumbItem {
  title: string
  path: string
}

interface BreadcrumbData {
  projectName?: string
  memberName?: string
  chapterName?: string
  committeeName?: string
  orgName?: string
  repoName?: string
}

export function useBreadcrumbs(breadcrumbData?: BreadcrumbData): BreadCrumbItem[] {
  const pathname = usePathname()
  const breadcrumbs: BreadCrumbItem[] = [{ title: 'Home', path: '/' }]

  if (!pathname) return breadcrumbs

  const segments = pathname.split('/').filter(Boolean)

  const isNestedRepoRoute =
    segments.length === 4 && segments[0] === 'organizations' && segments[2] === 'repositories'

  if (isNestedRepoRoute) {
    breadcrumbs.push({ title: 'Organizations', path: '/organizations' })

    const orgTitle = breadcrumbData?.orgName || upperFirst(segments[1]).replaceAll('-', ' ')
    breadcrumbs.push({
      title: orgTitle,
      path: `/organizations/${segments[1]}`,
    })

    const repoTitle = breadcrumbData?.repoName || upperFirst(segments[3]).replaceAll('-', ' ')
    breadcrumbs.push({
      title: repoTitle,
      path: `/organizations/${segments[1]}/repositories/${segments[3]}`,
    })
  } else {
    segments.forEach((segment, index) => {
      const isLastSegment = index === segments.length - 1
      const path = '/' + segments.slice(0, index + 1).join('/')

      let title = upperFirst(segment).replaceAll('-', ' ')

      if (isLastSegment && breadcrumbData) {
        title =
          breadcrumbData.projectName ||
          breadcrumbData.memberName ||
          breadcrumbData.chapterName ||
          breadcrumbData.committeeName ||
          breadcrumbData.orgName ||
          title
      }
      breadcrumbs.push({ title, path })
    })
  }

  return breadcrumbs
}
