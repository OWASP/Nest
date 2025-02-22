import { ChapterTypeAlgolia } from './chapter'
import { ProjectTypeAlgolia } from './project'
import { User } from './user'

export interface MultiSearchBarProps {
  isLoaded: boolean
  placeholder: string
  indexes: string[]
  initialValue?: string
}

export interface Suggestion {
  indexName: string
  hits: ChapterTypeAlgolia[] | ProjectTypeAlgolia[] | User[]
  totalPages: number
}
