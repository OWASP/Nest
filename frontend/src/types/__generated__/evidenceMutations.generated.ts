/** Internal type. DO NOT USE DIRECTLY. */
type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
/** Internal type. DO NOT USE DIRECTLY. */
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type CreateEvidenceInput = {
  claimKey: string;
  description: string;
  file?: any;
  name: string;
  sourceUrl?: string | null | undefined;
  year: number;
};

export type RemoveEvidenceInput = {
  claimKey: string;
  key: string;
  removedReason?: string | null | undefined;
  year: number;
};

export type UpdateEvidenceInput = {
  claimKey: string;
  description?: string | null | undefined;
  file?: any;
  key: string;
  name?: string | null | undefined;
  sourceUrl?: string | null | undefined;
  year: number;
};

export type CreateBoardCandidateClaimEvidenceMutationVariables = Exact<{
  input: Types.CreateEvidenceInput;
}>;


export type CreateBoardCandidateClaimEvidenceMutation = { createBoardCandidateClaimEvidence: { __typename: 'EvidenceResult', ok: boolean, code: string | null, message: string | null, evidence: { __typename: 'BoardCandidateClaimEvidenceNode', id: string, createdAt: any, description: string, hasFile: boolean, key: string, name: string, sourceUrl: string, updatedAt: any } | null } };

export type RemoveBoardCandidateClaimEvidenceMutationVariables = Exact<{
  input: Types.RemoveEvidenceInput;
}>;


export type RemoveBoardCandidateClaimEvidenceMutation = { removeBoardCandidateClaimEvidence: { __typename: 'EvidenceResult', ok: boolean, code: string | null, message: string | null, evidence: { __typename: 'BoardCandidateClaimEvidenceNode', id: string, createdAt: any, description: string, hasFile: boolean, key: string, name: string, sourceUrl: string, updatedAt: any } | null } };

export type UpdateBoardCandidateClaimEvidenceMutationVariables = Exact<{
  input: Types.UpdateEvidenceInput;
}>;


export type UpdateBoardCandidateClaimEvidenceMutation = { updateBoardCandidateClaimEvidence: { __typename: 'EvidenceResult', ok: boolean, code: string | null, message: string | null, evidence: { __typename: 'BoardCandidateClaimEvidenceNode', id: string, createdAt: any, description: string, hasFile: boolean, key: string, name: string, sourceUrl: string, updatedAt: any } | null } };


export const CreateBoardCandidateClaimEvidenceDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateBoardCandidateClaimEvidence"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateEvidenceInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createBoardCandidateClaimEvidence"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"evidence"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"hasFile"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"sourceUrl"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]}}]} as unknown as DocumentNode<CreateBoardCandidateClaimEvidenceMutation, CreateBoardCandidateClaimEvidenceMutationVariables>;
export const RemoveBoardCandidateClaimEvidenceDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"RemoveBoardCandidateClaimEvidence"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"RemoveEvidenceInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"removeBoardCandidateClaimEvidence"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"evidence"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"hasFile"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"sourceUrl"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]}}]} as unknown as DocumentNode<RemoveBoardCandidateClaimEvidenceMutation, RemoveBoardCandidateClaimEvidenceMutationVariables>;
export const UpdateBoardCandidateClaimEvidenceDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateBoardCandidateClaimEvidence"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateEvidenceInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateBoardCandidateClaimEvidence"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"evidence"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"hasFile"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"sourceUrl"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]}}]} as unknown as DocumentNode<UpdateBoardCandidateClaimEvidenceMutation, UpdateBoardCandidateClaimEvidenceMutationVariables>;