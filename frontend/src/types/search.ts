import { ChapterType } from 'types/chapter'
import { EventType } from 'types/event'
import { Organization } from 'types/organization'
import { ProjectType } from 'types/project'
import { User } from 'types/user'

export interface MultiSearchBarProps {
  isLoaded: boolean
  placeholder: string
  indexes: string[]
  initialValue?: string
  eventData?: EventType[]
}

export interface Suggestion {
  indexName: string
  hits: ChapterType[] | EventType[] | Organization[] | ProjectType[] | User[]
  totalPages: number
}
