import * as Types from '../../types/__generated__/graphql';

export type LogoutDjangoMutationVariables = Types.Exact<{ [key: string]: never; }>;


export type LogoutDjangoMutation = { logoutUser: { __typename: 'LogoutResult', code: string | null, message: string | null, ok: boolean } };

export type SyncDjangoSessionMutationVariables = Types.Exact<{
  accessToken: Types.Scalars['String']['input'];
}>;


export type SyncDjangoSessionMutation = { githubAuth: { __typename: 'GitHubAuthResult', message: string, ok: boolean, user: { __typename: 'AuthUserNode', isOwaspStaff: boolean } | null } };
