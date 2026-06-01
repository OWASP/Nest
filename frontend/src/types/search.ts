import type { Chapter } from 'types/chapter'
import type { Event } from 'types/event'
import type { Organization } from 'types/organization'
import type { Project } from 'types/project'
import type { User } from 'types/user'

export type Suggestion = {
  indexName: string
  hits: Chapter[] | Event[] | Organization[] | Project[] | User[]
  totalPages: number
}
