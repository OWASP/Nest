import * as Types from '../../types/__generated__/graphql';

export type GetSnapshotDetailsQueryVariables = Types.Exact<{
  key: Types.Scalars['String']['input'];
}>;


export type GetSnapshotDetailsQuery = { snapshot: { __typename: 'SnapshotNode', endAt: unknown, key: string, startAt: unknown, title: string, newReleases: Array<{ __typename: 'ReleaseNode', name: string, publishedAt: unknown | null, tagName: string, projectName: string | null }>, newProjects: Array<{ __typename: 'ProjectNode', key: string, name: string, summary: string, starsCount: number, forksCount: number, contributorsCount: number, level: string, isActive: boolean, repositoriesCount: number, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }> }>, newChapters: Array<{ __typename: 'ChapterNode', key: string, name: string, createdAt: number, suggestedLocation: string | null, region: string, summary: string, updatedAt: number, url: string, relatedUrls: Array<string>, isActive: boolean, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }>, geoLocation: { __typename: 'GeoLocationType', lat: number, lng: number } | null }> } | null };

export type GetSnapshotDetailsMetadataQueryVariables = Types.Exact<{
  key: Types.Scalars['String']['input'];
}>;


export type GetSnapshotDetailsMetadataQuery = { snapshot: { __typename: 'SnapshotNode', title: string } | null };

export type GetCommunitySnapshotsQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type GetCommunitySnapshotsQuery = { snapshots: Array<{ __typename: 'SnapshotNode', key: string, title: string, startAt: unknown, endAt: unknown }> };
