export const round = (value: number, precision = 2): number => {
  if (isNaN(value)) return 0 // Handle NaN values
  if (precision < 0) {
    throw new Error('Precision must be a non-negative integer')
  }
  const factor = Math.pow(10, precision)
  return Math.round(value * factor) / factor
}
