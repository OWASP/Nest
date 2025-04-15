import _ from 'lodash'

export const getProjectUrl = (url = ''): string => {
  const projectName = _.last(_.split(url, 'www-project-')) || ''
  return `/projects/${projectName}`
}

export const getMemberUrl = (loginName = ''): string => {
  return `/members/${loginName}`
}
