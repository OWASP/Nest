import { type ClassValue, clsx } from 'clsx'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { twMerge } from 'tailwind-merge'

import { CommitteeType } from 'types/committee'
import { IssueType } from 'types/issue'
import { project } from 'types/project'
import { IconType } from 'lib/constants'
import { IconKeys, Icons, urlMappings } from 'components/data'

dayjs.extend(relativeTime)

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

type projectType = project | IssueType | CommitteeType

export const getFilteredIcons = (project: projectType, params: string[]): IconType => {
  const filteredIcons = params.reduce((acc: IconType, key) => {
    if (Icons[key as IconKeys] && project[key as keyof typeof project] !== undefined) {
      if (key === 'idx_updated_at') {
        acc[key] = dayjs.unix(project[key] as number).fromNow()
      } else if (key === 'idx_created_at') {
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

export const removeIdxPrefix = (obj: IndexedObject): IndexedObject => {
  const newObj: IndexedObject = {}
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const newKey = key.startsWith('idx_') ? key.slice(4) : key
      newObj[newKey] = obj[key]
    }
  }
  return newObj
}
