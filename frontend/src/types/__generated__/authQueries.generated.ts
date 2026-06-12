import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type LogoutDjangoMutationVariables = Types.Exact<{ [key: string]: never; }>;


export type LogoutDjangoMutation = { logoutUser: { __typename: 'LogoutResult', code: string | null, message: string | null, ok: boolean } };

export type SyncDjangoSessionMutationVariables = Types.Exact<{
  accessToken: Types.Scalars['String']['input'];
}>;


export type SyncDjangoSessionMutation = { githubAuth: { __typename: 'GitHubAuthResult', message: string, ok: boolean, user: { __typename: 'AuthUserNode', id: string, isOwaspStaff: boolean } | null } };


export const LogoutDjangoDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"LogoutDjango"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"logoutUser"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"ok"}}]}}]}}]} as unknown as DocumentNode<LogoutDjangoMutation, LogoutDjangoMutationVariables>;
export const SyncDjangoSessionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SyncDjangoSession"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"accessToken"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"githubAuth"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"accessToken"},"value":{"kind":"Variable","name":{"kind":"Name","value":"accessToken"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isOwaspStaff"}}]}}]}}]}}]} as unknown as DocumentNode<SyncDjangoSessionMutation, SyncDjangoSessionMutationVariables>;