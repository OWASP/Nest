export function toApexTooltipTheme(
  resolvedTheme: string | undefined
): 'light' | 'dark' | undefined {
  if (resolvedTheme === 'light' || resolvedTheme === 'dark') {
    return resolvedTheme
  }

  return undefined
}
