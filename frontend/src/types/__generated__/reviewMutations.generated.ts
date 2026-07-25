/** Internal type. DO NOT USE DIRECTLY. */
type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
/** Internal type. DO NOT USE DIRECTLY. */
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type CreateReviewInput = {
  claimKey: string;
  claimMemberLogin: string;
  notes?: string;
  status: ReviewStatusEnum;
  year: number;
};

export type ReviewStatusEnum =
  | 'APPROVED'
  | 'REJECTED';

export type CreateBoardCandidateClaimReviewMutationVariables = Exact<{
  input: Types.CreateReviewInput;
}>;


export type CreateBoardCandidateClaimReviewMutation = { createBoardCandidateClaimReview: { __typename: 'ReviewResult', ok: boolean, code: string | null, message: string | null, review: { __typename: 'BoardCandidateClaimReviewNode', id: string, createdAt: any, notes: string, status: Types.ReviewStatusEnum } | null } };


export const CreateBoardCandidateClaimReviewDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateBoardCandidateClaimReview"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateReviewInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createBoardCandidateClaimReview"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"review"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"notes"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}}]}}]}}]} as unknown as DocumentNode<CreateBoardCandidateClaimReviewMutation, CreateBoardCandidateClaimReviewMutationVariables>;