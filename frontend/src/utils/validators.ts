export const validateTags = (tagsString: string): string | null => {
    if (!tagsString) return null

    const tags = tagsString.split(',').map((t) => t.trim()).filter(Boolean)

    // Check for duplicates
    const uniqueTags = new Set(tags)
    if (uniqueTags.size !== tags.length) {
        return 'Tags must be unique.'
    }

    // Check for alphanumeric (allow spaces, dashes, underscores)
    const regex = /^[a-zA-Z0-9\s\-_]+$/
    for (const tag of tags) {
        if (!regex.test(tag)) {
            return `Tag "${tag}" contains invalid characters. Only alphanumeric characters, spaces, dashes, and underscores are allowed.`
        }
    }

    return null
}
