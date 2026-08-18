/** Internal type. DO NOT USE DIRECTLY. */
type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
/** Internal type. DO NOT USE DIRECTLY. */
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type CreateSnapshotSubscriptionInput = {
  frequency?: SnapshotFrequency;
  includeChapters?: boolean;
  includeEvents?: boolean;
  includeIssues?: boolean;
  includePosts?: boolean;
  includeProjects?: boolean;
  includePullRequests?: boolean;
  includeReleases?: boolean;
  includeUsers?: boolean;
  name?: string;
  subscribedChapterIds?: Array<number> | null | undefined;
  subscribedCommitteeIds?: Array<number> | null | undefined;
  subscribedProjectIds?: Array<number> | null | undefined;
};

export type SnapshotFrequency =
  | 'MONTHLY'
  | 'WEEKLY';

export type UpdateSnapshotSubscriptionInput = {
  frequency?: SnapshotFrequency | null | undefined;
  includeChapters?: boolean | null | undefined;
  includeEvents?: boolean | null | undefined;
  includeIssues?: boolean | null | undefined;
  includePosts?: boolean | null | undefined;
  includeProjects?: boolean | null | undefined;
  includePullRequests?: boolean | null | undefined;
  includeReleases?: boolean | null | undefined;
  includeUsers?: boolean | null | undefined;
  name?: string | null | undefined;
  subscribedChapterIds?: Array<number> | null | undefined;
  subscribedCommitteeIds?: Array<number> | null | undefined;
  subscribedProjectIds?: Array<number> | null | undefined;
};

export type SnapshotSubscriptionFieldsFragment = { __typename: 'SnapshotSubscriptionNode', id: string, name: string, frequency: string, isActive: boolean, includeChapters: boolean, includeEvents: boolean, includeIssues: boolean, includePosts: boolean, includeProjects: boolean, includePullRequests: boolean, includeReleases: boolean, includeUsers: boolean, createdAt: any, updatedAt: any, subscribedProjects: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }>, subscribedChapters: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }>, subscribedCommittees: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }> };

export type GetMySnapshotSubscriptionsQueryVariables = Exact<{ [key: string]: never; }>;


export type GetMySnapshotSubscriptionsQuery = { mySnapshotSubscriptions: Array<{ __typename: 'SnapshotSubscriptionNode', id: string, name: string, frequency: string, isActive: boolean, includeChapters: boolean, includeEvents: boolean, includeIssues: boolean, includePosts: boolean, includeProjects: boolean, includePullRequests: boolean, includeReleases: boolean, includeUsers: boolean, createdAt: any, updatedAt: any, subscribedProjects: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }>, subscribedChapters: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }>, subscribedCommittees: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }> }> };

export type CreateSnapshotSubscriptionMutationVariables = Exact<{
  inputData: Types.CreateSnapshotSubscriptionInput;
}>;


export type CreateSnapshotSubscriptionMutation = { createSnapshotSubscription: { __typename: 'SnapshotSubscriptionResult', ok: boolean, message: string, subscription: { __typename: 'SnapshotSubscriptionNode', id: string, name: string, frequency: string, isActive: boolean, includeChapters: boolean, includeEvents: boolean, includeIssues: boolean, includePosts: boolean, includeProjects: boolean, includePullRequests: boolean, includeReleases: boolean, includeUsers: boolean, createdAt: any, updatedAt: any, subscribedProjects: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }>, subscribedChapters: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }>, subscribedCommittees: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }> } | null } };

export type UpdateSnapshotSubscriptionMutationVariables = Exact<{
  subscriptionId: number;
  inputData: Types.UpdateSnapshotSubscriptionInput;
}>;


export type UpdateSnapshotSubscriptionMutation = { updateSnapshotSubscription: { __typename: 'SnapshotSubscriptionResult', ok: boolean, message: string, subscription: { __typename: 'SnapshotSubscriptionNode', id: string, name: string, frequency: string, isActive: boolean, includeChapters: boolean, includeEvents: boolean, includeIssues: boolean, includePosts: boolean, includeProjects: boolean, includePullRequests: boolean, includeReleases: boolean, includeUsers: boolean, createdAt: any, updatedAt: any, subscribedProjects: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }>, subscribedChapters: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }>, subscribedCommittees: Array<{ __typename: 'SubscribedEntityNode', id: number, name: string }> } | null } };

export type CancelSnapshotSubscriptionMutationVariables = Exact<{
  subscriptionId: number;
}>;


export type CancelSnapshotSubscriptionMutation = { cancelSnapshotSubscription: { __typename: 'SnapshotSubscriptionResult', ok: boolean, message: string, subscription: { __typename: 'SnapshotSubscriptionNode', id: string, isActive: boolean } | null } };

export type DeleteSnapshotSubscriptionMutationVariables = Exact<{
  subscriptionId: number;
}>;


export type DeleteSnapshotSubscriptionMutation = { deleteSnapshotSubscription: { __typename: 'SnapshotSubscriptionResult', ok: boolean, message: string } };

export type ReactivateSnapshotSubscriptionMutationVariables = Exact<{
  subscriptionId: number;
}>;


export type ReactivateSnapshotSubscriptionMutation = { reactivateSnapshotSubscription: { __typename: 'SnapshotSubscriptionResult', ok: boolean, message: string, subscription: { __typename: 'SnapshotSubscriptionNode', id: string, isActive: boolean } | null } };


export const GetMySnapshotSubscriptionsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetMySnapshotSubscriptions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"mySnapshotSubscriptions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"SnapshotSubscriptionFields"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SnapshotSubscriptionFields"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"SnapshotSubscriptionNode"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"frequency"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}},{"kind":"Field","name":{"kind":"Name","value":"includeChapters"}},{"kind":"Field","name":{"kind":"Name","value":"includeEvents"}},{"kind":"Field","name":{"kind":"Name","value":"includeIssues"}},{"kind":"Field","name":{"kind":"Name","value":"includePosts"}},{"kind":"Field","name":{"kind":"Name","value":"includeProjects"}},{"kind":"Field","name":{"kind":"Name","value":"includePullRequests"}},{"kind":"Field","name":{"kind":"Name","value":"includeReleases"}},{"kind":"Field","name":{"kind":"Name","value":"includeUsers"}},{"kind":"Field","name":{"kind":"Name","value":"subscribedProjects"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"subscribedChapters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"subscribedCommittees"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]} as unknown as DocumentNode<GetMySnapshotSubscriptionsQuery, GetMySnapshotSubscriptionsQueryVariables>;
export const CreateSnapshotSubscriptionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateSnapshotSubscription"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"inputData"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateSnapshotSubscriptionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createSnapshotSubscription"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"inputData"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"subscription"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"SnapshotSubscriptionFields"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SnapshotSubscriptionFields"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"SnapshotSubscriptionNode"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"frequency"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}},{"kind":"Field","name":{"kind":"Name","value":"includeChapters"}},{"kind":"Field","name":{"kind":"Name","value":"includeEvents"}},{"kind":"Field","name":{"kind":"Name","value":"includeIssues"}},{"kind":"Field","name":{"kind":"Name","value":"includePosts"}},{"kind":"Field","name":{"kind":"Name","value":"includeProjects"}},{"kind":"Field","name":{"kind":"Name","value":"includePullRequests"}},{"kind":"Field","name":{"kind":"Name","value":"includeReleases"}},{"kind":"Field","name":{"kind":"Name","value":"includeUsers"}},{"kind":"Field","name":{"kind":"Name","value":"subscribedProjects"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"subscribedChapters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"subscribedCommittees"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]} as unknown as DocumentNode<CreateSnapshotSubscriptionMutation, CreateSnapshotSubscriptionMutationVariables>;
export const UpdateSnapshotSubscriptionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateSnapshotSubscription"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"subscriptionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"inputData"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateSnapshotSubscriptionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateSnapshotSubscription"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"subscriptionId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"subscriptionId"}}},{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"inputData"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"subscription"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"SnapshotSubscriptionFields"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SnapshotSubscriptionFields"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"SnapshotSubscriptionNode"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"frequency"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}},{"kind":"Field","name":{"kind":"Name","value":"includeChapters"}},{"kind":"Field","name":{"kind":"Name","value":"includeEvents"}},{"kind":"Field","name":{"kind":"Name","value":"includeIssues"}},{"kind":"Field","name":{"kind":"Name","value":"includePosts"}},{"kind":"Field","name":{"kind":"Name","value":"includeProjects"}},{"kind":"Field","name":{"kind":"Name","value":"includePullRequests"}},{"kind":"Field","name":{"kind":"Name","value":"includeReleases"}},{"kind":"Field","name":{"kind":"Name","value":"includeUsers"}},{"kind":"Field","name":{"kind":"Name","value":"subscribedProjects"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"subscribedChapters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"subscribedCommittees"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]} as unknown as DocumentNode<UpdateSnapshotSubscriptionMutation, UpdateSnapshotSubscriptionMutationVariables>;
export const CancelSnapshotSubscriptionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CancelSnapshotSubscription"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"subscriptionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"cancelSnapshotSubscription"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"subscriptionId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"subscriptionId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"subscription"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}}]}}]}}]}}]} as unknown as DocumentNode<CancelSnapshotSubscriptionMutation, CancelSnapshotSubscriptionMutationVariables>;
export const DeleteSnapshotSubscriptionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteSnapshotSubscription"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"subscriptionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteSnapshotSubscription"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"subscriptionId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"subscriptionId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<DeleteSnapshotSubscriptionMutation, DeleteSnapshotSubscriptionMutationVariables>;
export const ReactivateSnapshotSubscriptionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"ReactivateSnapshotSubscription"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"subscriptionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"reactivateSnapshotSubscription"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"subscriptionId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"subscriptionId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"subscription"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}}]}}]}}]}}]} as unknown as DocumentNode<ReactivateSnapshotSubscriptionMutation, ReactivateSnapshotSubscriptionMutationVariables>;