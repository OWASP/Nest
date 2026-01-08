export default function slugify(text: string): string {
  return text
    .normalize('NFKD') // Normalize accented characters
    .replaceAll(/[\u0300-\u036F]/g, '') // Remove diacritics
    .replaceAll(/[^a-zA-Z0-9]+/g, '-') // Replace non-alphanumeric with hyphens
    .replace(/^[-]+/, '') // Trim leading hyphens
    .replace(/[-]+$/, '') // Trim trailing hyphens
    .toLowerCase()
}
