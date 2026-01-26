export const getMemberUrl = (login: string): string => `/members/${login}`
export const getProjectUrl = (projectKey: string): string => `/projects/${projectKey}`
export const getMenteeUrl = (programKey: string, moduleKey: string, login: string): string =>
  `/my/mentorship/programs/${programKey}/modules/${moduleKey}/mentees/${login}`
