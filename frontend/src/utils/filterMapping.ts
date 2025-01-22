export const getParamsForFilters = (indexName: string, filter: string) => {
  filter = filter.trim()
  switch (indexName) {
    case 'projects':
      switch (true) {
        case /^contributors([><]=?|=)(\d+)$/.test(filter):
          return filter.replace(/^contributors([><]=?|=)(\d+)$/, 'idx_contributors_count$1$2')
        case /^stars([><]=?|=)(\d+)$/.test(filter):
          return filter.replace(/^stars([><]=?|=)(\d+)$/, 'idx_stars_count$1$2')
        case /^forks([><]=?|=)(\d+)$/.test(filter):
          return filter.replace(/^forks([><]=?|=)(\d+)$/, 'idx_forks_count$1$2')
        case /^is:([a-zA-Z]+)$/.test(filter):
          return filter.replace(/^is:([a-zA-Z]+)$/, 'idx_type:$1')
        default:
          return filter
      }
    default:
      return filter
  }
}
