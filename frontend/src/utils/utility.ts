import { type ClassValue, clsx } from 'clsx'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { twMerge } from 'tailwind-merge'
import { fetchCsrfToken } from 'server/fetchCsrfToken'

import type { Chapter } from 'types/chapter'
import type { Committee } from 'types/committee'
import type { Icon } from 'types/icon'
import type { Issue } from 'types/issue'
import type { Project } from 'types/project'
import { IconKeys, Icons, urlMappings } from 'utils/data'

dayjs.extend(relativeTime)

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

type projectType = Project | Issue | Committee | Chapter

export const getFilteredIcons = (project: projectType, params: string[]): Icon => {
  const filteredIcons = params.reduce((acc: Icon, key) => {
    if (Icons[key as IconKeys] && project[key as keyof typeof project] !== undefined) {
      if (key === 'createdAt') {
        acc[key] = dayjs.unix(project[key as keyof projectType] as unknown as number).fromNow()
      } else {
        acc[key] = project[key as keyof typeof project] as unknown as number
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

export const getCsrfToken = async (): Promise<string> => {
  const csrfToken = document.cookie
    ? document.cookie
        .split(';')
        .map((cookie) => cookie.split('='))
        .find(([key]) => key.trim() === 'csrftoken')?.[1]
        ?.trim()
    : undefined

  if (csrfToken) {
    return csrfToken
  }

  return await fetchCsrfToken()
}
