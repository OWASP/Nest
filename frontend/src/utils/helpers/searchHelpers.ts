export const isValidSearchQuery = (query: string) => /^[a-zA-Z0-9 _-]+$/.test(query)
