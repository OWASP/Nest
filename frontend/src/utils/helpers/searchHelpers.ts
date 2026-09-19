export const isValidSearchQuery = (query: string) => /^[a-zA-Z0-9\s\-_]+$/.test(query)
