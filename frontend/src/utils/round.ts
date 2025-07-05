export const round = (value: number, precision = 2): number => {
  if (isNaN(value)) return 0 // Handle NaN values
  const factor = Math.pow(10, precision)
  return Math.round(value * factor) / factor
}
