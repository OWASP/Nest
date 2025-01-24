import { createListCollection } from '@chakra-ui/react'

export const sortOptionsProject = createListCollection({
  items: [
    { label: 'Default', value: 'default' },
    { label: 'Name', value: 'name' },
    { label: 'Stars', value: 'stars_count' },
    { label: 'Contributors', value: 'contributors_count' },
    { label: 'Forks', value: 'forks_count' },
  ],
})

export const sortOrderOptions = createListCollection({
  items: [
    { label: 'Asc', value: 'asc' },
    { label: 'Desc', value: 'desc' },
  ],
})
