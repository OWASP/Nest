export const getParamsForIndexName = (indexName: string, distinct = false) => {
  switch (indexName) {
    case 'issues':
      return {
        attributesToRetrieve: [
          'idx_comments_count',
          'idx_created_at',
          'idx_hint',
          'idx_labels',
          'idx_project_name',
          'idx_project_url',
          'idx_repository_languages',
          'idx_summary',
          'idx_title',
          'idx_updated_at',
          'idx_url',
        ],
        distinct: distinct ? 1 : 0,
      }

    case 'chapters':
      return {
        attributesToRetrieve: [
          'idx_created_at',
          'idx_leaders',
          'idx_name',
          'idx_related_urls',
          'idx_summary',
          'idx_top_contributors',
          'idx_updated_at',
          'idx_url',
        ],
        aroundLatLngViaIP: true,
        typoTolerance: 'min',
        minProximity: 4,
      }

    case 'projects':
      return {
        attributesToRetrieve: [
          'idx_contributors_count',
          'idx_forks_count',
          'idx_leaders',
          'idx_level',
          'idx_name',
          'idx_stars_count',
          'idx_summary',
          'idx_top_contributors',
          'idx_topics',
          'idx_type',
          'idx_updated_at',
          'idx_url',
        ],
        typoTolerance: 'min',
        minProximity: 4,
      }
    case 'committees':
      return {
        attributesToRetrieve: [
          'idx_created_at',
          'idx_leaders',
          'idx_name',
          'idx_related_urls',
          'idx_summary',
          'idx_top_contributors',
          'idx_updated_at',
          'idx_url',
        ],
        typoTolerance: 'min',
        minProximity: 4,
      }
  }
}
