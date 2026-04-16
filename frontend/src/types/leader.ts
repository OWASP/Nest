export type Leader = {
  description: string
  memberName: string
  member: {
    login: string
    name: string
    avatarUrl: string
  } | null
}
