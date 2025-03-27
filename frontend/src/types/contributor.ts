export type TopContributorsTypeAlgolia = {
  avatar_url: string
  contributions_count: number
  login: string
  name: string
}

export type TopContributorsTypeGraphql = {
  avatarUrl: string
  contributionsCount: number
  login: string
  name: string
  projectName?: string
  projectUrl?: string
}
