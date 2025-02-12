export const pluralize = (count?: number, forms = 's'): string => {
  const parts = forms.split(',')
  if (!count && parts.length === 1) return parts[0]

  if (parts.length === 1) {
    return count === 1 ? '' : parts[0]
  }
  return count === 1 ? parts[0] : parts[1]
}
