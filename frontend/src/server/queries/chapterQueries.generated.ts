import * as Types from '../../types/__generated__/graphql';

export type GetChapterDataQueryVariables = Types.Exact<{
  key: Types.Scalars['String']['input'];
}>;


export type GetChapterDataQuery = { chapter: { __typename: 'ChapterNode', isActive: boolean, key: string, name: string, region: string, relatedUrls: Array<string>, suggestedLocation: string | null, summary: string, updatedAt: number, url: string, geoLocation: { __typename: 'GeoLocationType', lat: number, lng: number } | null } | null, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }> };

export type GetChapterMetadataQueryVariables = Types.Exact<{
  key: Types.Scalars['String']['input'];
}>;


export type GetChapterMetadataQuery = { chapter: { __typename: 'ChapterNode', name: string, summary: string } | null };
