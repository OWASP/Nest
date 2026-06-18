/** Escape text for ICS property values (RFC 5545). Matches `ics` package `format-text` behavior. */
export default function formatIcsText(text: string): string {
  return text
    .replaceAll('\\', '\\\\')
    .replace(/\r?\n/g, '\\n') // NOSONAR — matches ics `format-text` newline handling
    .replaceAll(';', String.raw`\;`)
    .replaceAll(',', String.raw`\,`)
}
