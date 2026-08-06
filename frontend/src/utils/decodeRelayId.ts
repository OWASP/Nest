export function decodeRelayId(globalId: string): number {
  const asInt = Number.parseInt(globalId, 10)
  if (!Number.isNaN(asInt)) {
    return asInt
  }
  try {
    const decoded = atob(globalId)
    const parts = decoded.split(':')
    const parsed = Number.parseInt(parts.at(-1)!, 10)
    if (!Number.isNaN(parsed)) {
      return parsed
    }
  } catch {
    // Fall through to regex match
  }
  const match = /\d+/.exec(globalId)
  return match ? Number.parseInt(match[0], 10) : 0
}
