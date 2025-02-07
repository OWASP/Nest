import { type ClassValue, clsx } from 'clsx'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { twMerge } from 'tailwind-merge'

import { CommitteeTypeAlgolia } from 'types/committee'
import { IconType } from 'types/icon'
import { IssueType } from 'types/issue'
import { ProjectTypeAlgolia } from 'types/project'
import { IconKeys, Icons, urlMappings } from 'utils/data'

dayjs.extend(relativeTime)

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

type projectType = ProjectTypeAlgolia | IssueType | CommitteeTypeAlgolia

export const getFilteredIcons = (project: projectType, params: string[]): IconType => {
  const filteredIcons = params.reduce((acc: IconType, key) => {
    if (Icons[key as IconKeys] && project[key as keyof typeof project] !== undefined) {
      if (key === 'updated_at') {
        acc[key] = dayjs.unix(project[key] as number).fromNow()
      } else if (key === 'created_at') {
        acc[key] = dayjs.unix(project[key as keyof projectType] as number).fromNow()
      } else {
        acc[key] = project[key as keyof typeof project] as number
      }
    }
    return acc
  }, {})

  return filteredIcons
}

export const handleSocialUrls = (related_urls: string[]) => {
  return related_urls.map((url) => {
    const match = urlMappings.find((mapping) => url.includes(mapping.key))

    return match
      ? { title: match.title, icon: match.icon, url }
      : { title: 'Social Links', icon: 'fa-solid fa-globe', url }
  })
}

export type IndexedObject = {
  [key: string]: unknown
}
