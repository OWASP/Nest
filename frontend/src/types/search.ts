import { ChapterTypeAlgolia } from './chapter'
import { EventType } from './event'
import { OrganizationTypeAlgolia } from './organization'
import { ProjectTypeAlgolia } from './project'
import { User } from './user'

export interface MultiSearchBarProps {
  isLoaded: boolean
  placeholder: string
  indexes: string[]
  initialValue?: string
  eventData?: EventType[]
}

export interface Suggestion {
  indexName: string
  hits:
    | ChapterTypeAlgolia[]
    | EventType[]
    | OrganizationTypeAlgolia[]
    | ProjectTypeAlgolia[]
    | User[]
  totalPages: number
}
