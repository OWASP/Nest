import { createListCollection } from "@chakra-ui/react";

export const sortOptionsProject = createListCollection({
  items: [
    { label: 'Default', value: '' },
    { label: 'Name (A-Z)', value: 'name_asc' },
    { label: 'Name (Z-A)', value: 'name_desc' },
    { label: 'Stars (Low to High)', value: 'stars_count_asc' },
    { label: 'Stars (High to Low)', value: 'stars_count_desc' },
    { label: 'Contributors (Low to High)', value: 'contributors_count_asc' },
    { label: 'Contributors (High to Low)', value: 'contributors_count_desc' },
    { label: 'Forks (Low to High)', value: 'forks_count_asc' },
    { label: 'Forks (High to Low)', value: 'forks_count_desc' },
  ],
})
