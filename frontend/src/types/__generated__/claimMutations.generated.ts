/** Internal type. DO NOT USE DIRECTLY. */
type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
/** Internal type. DO NOT USE DIRECTLY. */
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type ClaimStatusEnum =
  | 'APPROVED'
  | 'DISCARDED'
  | 'DRAFT'
  | 'REJECTED'
  | 'SUBMITTED'
  | 'WITHDRAWN';

export type CreateClaimInput = {
  description: string;
  name: string;
  year: number;
};

export type DiscardClaimInput = {
  key: string;
  year: number;
};

export type ReorderClaimsInput = {
  keys: Array<string>;
  year: number;
};

export type SubmitClaimInput = {
  key: string;
  year: number;
};

export type UpdateClaimInput = {
  description?: string | null | undefined;
  key: string;
  name?: string | null | undefined;
  year: number;
};

export type WithdrawClaimInput = {
  key: string;
  withdrawnReason: string;
  year: number;
};

export type CreateBoardCandidateClaimMutationVariables = Exact<{
  input: Types.CreateClaimInput;
}>;


export type CreateBoardCandidateClaimMutation = { createBoardCandidateClaim: { __typename: 'ClaimResult', ok: boolean, code: string | null, message: string | null, claim: { __typename: 'BoardCandidateClaimNode', createdAt: any, description: string, hasEvidence: boolean, id: string, key: string, name: string, order: number, status: Types.ClaimStatusEnum, updatedAt: any } | null } };

export type UpdateBoardCandidateClaimMutationVariables = Exact<{
  input: Types.UpdateClaimInput;
}>;


export type UpdateBoardCandidateClaimMutation = { updateBoardCandidateClaim: { __typename: 'ClaimResult', ok: boolean, code: string | null, message: string | null, claim: { __typename: 'BoardCandidateClaimNode', createdAt: any, description: string, hasEvidence: boolean, id: string, key: string, name: string, order: number, status: Types.ClaimStatusEnum, updatedAt: any } | null } };

export type DiscardBoardCandidateClaimMutationVariables = Exact<{
  input: Types.DiscardClaimInput;
}>;


export type DiscardBoardCandidateClaimMutation = { discardBoardCandidateClaim: { __typename: 'ClaimResult', ok: boolean, code: string | null, message: string | null, claim: { __typename: 'BoardCandidateClaimNode', createdAt: any, description: string, hasEvidence: boolean, id: string, key: string, name: string, order: number, status: Types.ClaimStatusEnum, updatedAt: any } | null } };

export type SubmitBoardCandidateClaimMutationVariables = Exact<{
  input: Types.SubmitClaimInput;
}>;


export type SubmitBoardCandidateClaimMutation = { submitBoardCandidateClaim: { __typename: 'ClaimResult', ok: boolean, code: string | null, message: string | null, claim: { __typename: 'BoardCandidateClaimNode', createdAt: any, description: string, hasEvidence: boolean, id: string, key: string, name: string, order: number, status: Types.ClaimStatusEnum, updatedAt: any } | null } };

export type WithdrawBoardCandidateClaimMutationVariables = Exact<{
  input: Types.WithdrawClaimInput;
}>;


export type WithdrawBoardCandidateClaimMutation = { withdrawBoardCandidateClaim: { __typename: 'ClaimResult', ok: boolean, code: string | null, message: string | null, claim: { __typename: 'BoardCandidateClaimNode', createdAt: any, description: string, hasEvidence: boolean, id: string, key: string, name: string, order: number, status: Types.ClaimStatusEnum, updatedAt: any } | null } };

export type ReorderBoardCandidateClaimsMutationVariables = Exact<{
  input: Types.ReorderClaimsInput;
}>;


export type ReorderBoardCandidateClaimsMutation = { reorderBoardCandidateClaims: { __typename: 'ReorderClaimsResult', ok: boolean, code: string | null, message: string | null, claims: Array<{ __typename: 'BoardCandidateClaimNode', createdAt: any, description: string, hasEvidence: boolean, id: string, key: string, name: string, order: number, status: Types.ClaimStatusEnum, updatedAt: any }> | null } };


export const CreateBoardCandidateClaimDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateBoardCandidateClaim"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateClaimInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createBoardCandidateClaim"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"claim"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"hasEvidence"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"order"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]}}]} as unknown as DocumentNode<CreateBoardCandidateClaimMutation, CreateBoardCandidateClaimMutationVariables>;
export const UpdateBoardCandidateClaimDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateBoardCandidateClaim"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateClaimInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateBoardCandidateClaim"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"claim"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"hasEvidence"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"order"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]}}]} as unknown as DocumentNode<UpdateBoardCandidateClaimMutation, UpdateBoardCandidateClaimMutationVariables>;
export const DiscardBoardCandidateClaimDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DiscardBoardCandidateClaim"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DiscardClaimInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"discardBoardCandidateClaim"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"claim"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"hasEvidence"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"order"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]}}]} as unknown as DocumentNode<DiscardBoardCandidateClaimMutation, DiscardBoardCandidateClaimMutationVariables>;
export const SubmitBoardCandidateClaimDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SubmitBoardCandidateClaim"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"SubmitClaimInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"submitBoardCandidateClaim"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"claim"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"hasEvidence"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"order"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]}}]} as unknown as DocumentNode<SubmitBoardCandidateClaimMutation, SubmitBoardCandidateClaimMutationVariables>;
export const WithdrawBoardCandidateClaimDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"WithdrawBoardCandidateClaim"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"WithdrawClaimInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"withdrawBoardCandidateClaim"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"claim"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"hasEvidence"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"order"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]}}]} as unknown as DocumentNode<WithdrawBoardCandidateClaimMutation, WithdrawBoardCandidateClaimMutationVariables>;
export const ReorderBoardCandidateClaimsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"ReorderBoardCandidateClaims"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ReorderClaimsInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"reorderBoardCandidateClaims"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"claims"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"hasEvidence"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"order"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]}}]} as unknown as DocumentNode<ReorderBoardCandidateClaimsMutation, ReorderBoardCandidateClaimsMutationVariables>;