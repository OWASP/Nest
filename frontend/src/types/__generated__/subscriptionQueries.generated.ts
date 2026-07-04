/** Internal type. DO NOT USE DIRECTLY. */
type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
/** Internal type. DO NOT USE DIRECTLY. */
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type CreateSnapshotSubscriptionInput = {
  frequency?: string;
  includeChapters?: boolean;
  includeEvents?: boolean;
  includePosts?: boolean;
  includeUsers?: boolean;
  projectPreferences?: Array<ProjectPreferenceInput> | null | undefined;
  subscribedChapterIds?: Array<number> | null | undefined;
};

export type ProjectPreferenceInput = {
  includeIssues?: boolean;
  includePullRequests?: boolean;
  includeReleases?: boolean;
  projectId: number;
};

export type UpdateSnapshotSubscriptionInput = {
  frequency?: string | null | undefined;
  includeChapters?: boolean | null | undefined;
  includeEvents?: boolean | null | undefined;
  includePosts?: boolean | null | undefined;
  includeUsers?: boolean | null | undefined;
  projectPreferences?: Array<ProjectPreferenceInput> | null | undefined;
  subscribedChapterIds?: Array<number> | null | undefined;
};

export type GetMySubscriptionQueryVariables = Exact<{ [key: string]: never; }>;


export type GetMySubscriptionQuery = { mySubscription: { __typename: 'SnapshotSubscriptionNode', id: string, frequency: string, isActive: boolean, includeChapters: boolean, includeEvents: boolean, includePosts: boolean, includeUsers: boolean, createdAt: any, updatedAt: any, projectPreferences: Array<{ __typename: 'ProjectSubscriptionPreferenceNode', id: string, includeIssues: boolean, includePullRequests: boolean, includeReleases: boolean, project: { __typename: 'ProjectNode', id: string, name: string } }>, chapters: Array<{ __typename: 'ChapterNode', id: string, name: string }> } | null };

export type CreateSnapshotSubscriptionMutationVariables = Exact<{
  inputData: Types.CreateSnapshotSubscriptionInput;
}>;


export type CreateSnapshotSubscriptionMutation = { createSnapshotSubscription: { __typename: 'SnapshotSubscriptionResult', ok: boolean, message: string, subscription: { __typename: 'SnapshotSubscriptionNode', id: string, frequency: string, isActive: boolean, includeChapters: boolean, includeEvents: boolean, includePosts: boolean, includeUsers: boolean, createdAt: any, updatedAt: any, projectPreferences: Array<{ __typename: 'ProjectSubscriptionPreferenceNode', id: string, includeIssues: boolean, includePullRequests: boolean, includeReleases: boolean, project: { __typename: 'ProjectNode', id: string, name: string } }>, chapters: Array<{ __typename: 'ChapterNode', id: string, name: string }> } | null } };

export type UpdateSnapshotSubscriptionMutationVariables = Exact<{
  inputData: Types.UpdateSnapshotSubscriptionInput;
}>;


export type UpdateSnapshotSubscriptionMutation = { updateSnapshotSubscription: { __typename: 'SnapshotSubscriptionResult', ok: boolean, message: string, subscription: { __typename: 'SnapshotSubscriptionNode', id: string, frequency: string, isActive: boolean, includeChapters: boolean, includeEvents: boolean, includePosts: boolean, includeUsers: boolean, createdAt: any, updatedAt: any, projectPreferences: Array<{ __typename: 'ProjectSubscriptionPreferenceNode', id: string, includeIssues: boolean, includePullRequests: boolean, includeReleases: boolean, project: { __typename: 'ProjectNode', id: string, name: string } }>, chapters: Array<{ __typename: 'ChapterNode', id: string, name: string }> } | null } };

export type CancelSnapshotSubscriptionMutationVariables = Exact<{ [key: string]: never; }>;


export type CancelSnapshotSubscriptionMutation = { cancelSnapshotSubscription: { __typename: 'SnapshotSubscriptionResult', ok: boolean, message: string, subscription: { __typename: 'SnapshotSubscriptionNode', id: string, isActive: boolean } | null } };


export const GetMySubscriptionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetMySubscription"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"mySubscription"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"frequency"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}},{"kind":"Field","name":{"kind":"Name","value":"includeChapters"}},{"kind":"Field","name":{"kind":"Name","value":"includeEvents"}},{"kind":"Field","name":{"kind":"Name","value":"includePosts"}},{"kind":"Field","name":{"kind":"Name","value":"includeUsers"}},{"kind":"Field","name":{"kind":"Name","value":"projectPreferences"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"project"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"includeIssues"}},{"kind":"Field","name":{"kind":"Name","value":"includePullRequests"}},{"kind":"Field","name":{"kind":"Name","value":"includeReleases"}}]}},{"kind":"Field","name":{"kind":"Name","value":"chapters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]} as unknown as DocumentNode<GetMySubscriptionQuery, GetMySubscriptionQueryVariables>;
export const CreateSnapshotSubscriptionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateSnapshotSubscription"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"inputData"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateSnapshotSubscriptionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createSnapshotSubscription"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"inputData"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"subscription"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"frequency"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}},{"kind":"Field","name":{"kind":"Name","value":"includeChapters"}},{"kind":"Field","name":{"kind":"Name","value":"includeEvents"}},{"kind":"Field","name":{"kind":"Name","value":"includePosts"}},{"kind":"Field","name":{"kind":"Name","value":"includeUsers"}},{"kind":"Field","name":{"kind":"Name","value":"projectPreferences"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"project"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"includeIssues"}},{"kind":"Field","name":{"kind":"Name","value":"includePullRequests"}},{"kind":"Field","name":{"kind":"Name","value":"includeReleases"}}]}},{"kind":"Field","name":{"kind":"Name","value":"chapters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]}}]} as unknown as DocumentNode<CreateSnapshotSubscriptionMutation, CreateSnapshotSubscriptionMutationVariables>;
export const UpdateSnapshotSubscriptionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateSnapshotSubscription"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"inputData"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateSnapshotSubscriptionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateSnapshotSubscription"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"inputData"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"subscription"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"frequency"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}},{"kind":"Field","name":{"kind":"Name","value":"includeChapters"}},{"kind":"Field","name":{"kind":"Name","value":"includeEvents"}},{"kind":"Field","name":{"kind":"Name","value":"includePosts"}},{"kind":"Field","name":{"kind":"Name","value":"includeUsers"}},{"kind":"Field","name":{"kind":"Name","value":"projectPreferences"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"project"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"includeIssues"}},{"kind":"Field","name":{"kind":"Name","value":"includePullRequests"}},{"kind":"Field","name":{"kind":"Name","value":"includeReleases"}}]}},{"kind":"Field","name":{"kind":"Name","value":"chapters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]}}]} as unknown as DocumentNode<UpdateSnapshotSubscriptionMutation, UpdateSnapshotSubscriptionMutationVariables>;
export const CancelSnapshotSubscriptionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CancelSnapshotSubscription"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"cancelSnapshotSubscription"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"subscription"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}}]}}]}}]}}]} as unknown as DocumentNode<CancelSnapshotSubscriptionMutation, CancelSnapshotSubscriptionMutationVariables>;