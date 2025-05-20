import { ChapterTypeAlgolia } from 'types/chapter'
import { EventType } from 'types/event'
import { OrganizationTypeAlgolia } from 'types/organization'
import { ProjectTypeAlgolia } from 'types/project'
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
  hits:
    | ChapterTypeAlgolia[]
    | EventType[]
    | OrganizationTypeAlgolia[]
    | ProjectTypeAlgolia[]
    | User[]
  totalPages: number
}
