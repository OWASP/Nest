import type { User } from 'types/user'

export type CertificateProject = {
  name: string
  key: string
}

export type CertificateChapter = {
  name: string
  key: string
}

export type Certificate = {
  id: string
  githubUser: User
  issuedAt: string
  isVerified: boolean
  score?: number | null
  tier?: string | null
  title?: string | null
  message?: string | null
  project?: CertificateProject | null
  chapter?: CertificateChapter | null
}
