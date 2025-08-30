import * as Types from '../../types/__generated__/graphql';

export type GetCommitteeDataQueryVariables = Types.Exact<{
  key: Types.Scalars['String']['input'];
}>;


export type GetCommitteeDataQuery = { committee: { __typename: 'CommitteeNode', contributorsCount: number, createdAt: number, forksCount: number, issuesCount: number, leaders: Array<string>, name: string, relatedUrls: Array<string>, repositoriesCount: number, starsCount: number, summary: string, updatedAt: number, url: string } | null, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }> };

export type GetCommitteeMetadataQueryVariables = Types.Exact<{
  key: Types.Scalars['String']['input'];
}>;


export type GetCommitteeMetadataQuery = { committee: { __typename: 'CommitteeNode', name: string, summary: string } | null };
