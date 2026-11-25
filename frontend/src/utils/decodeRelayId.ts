const INTEGER_PATTERN = /^\d+$/
const RELAY_GLOBAL_ID_PATTERN = /^[^:]+:(\d+)$/

export function decodeRelayId(globalId: string): number {
  if (INTEGER_PATTERN.test(globalId)) {
    return Number.parseInt(globalId, 10)
  }

  let decoded = ''
  try {
    decoded = atob(globalId)
  } catch {
    // Not valid base64; handled below.
  }

  const match = RELAY_GLOBAL_ID_PATTERN.exec(decoded)
  if (!match) {
    throw new Error(`Invalid Relay ID: ${globalId}`)
  }
  return Number.parseInt(match[1], 10)
}

export function tryDecodeRelayId(globalId: string): number | null {
  try {
    return decodeRelayId(globalId)
  } catch {
    return null
  }
}
