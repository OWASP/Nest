export default function slugify(text: string): string {
  return text
    .normalize('NFKD') // Normalize accented characters
    .replace(/[\u0300-\u036F]/g, '') // Remove diacritics
    .replace(/[^a-zA-Z0-9]+/g, '-') // Only allow letters and numbers, replace others with hyphen
    .replace(/^-+|-+$/g, '') // Trim leading/trailing hyphens
    .toLowerCase()
}
