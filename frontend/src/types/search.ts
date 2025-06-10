import { ChapterType } from 'types/chapter'
import { EventType } from 'types/event'
import { OrganizationType } from 'types/organization'
import { ProjectType } from 'types/project'
import { User } from 'types/user'

export interface MultiSearchBarProps {
  isLoaded: boolean
  placeholder: string
  indexes: string[]
  initialValue?: string
  eventData?: EventType[]
}

export type Suggestion = {
  indexName: string
  hits: ChapterType[] | EventType[] | OrganizationType[] | ProjectType[] | User[]
  totalPages: number
}
