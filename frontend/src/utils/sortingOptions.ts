import { createListCollection } from '@chakra-ui/react'

export const sortOptionsProject = createListCollection({
  items: [
    { label: 'Relevancy', value: 'default' },
    { label: 'Contributors', value: 'contributors_count' },
    { label: 'Forks', value: 'forks_count' },
    { label: 'Name', value: 'name' },
    { label: 'Stars', value: 'stars_count' },
  ],
})
