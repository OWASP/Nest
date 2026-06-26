/** Internal type. DO NOT USE DIRECTLY. */
type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
/** Internal type. DO NOT USE DIRECTLY. */
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type CreateProgramInput = {
  description: string;
  domains?: Array<string>;
  endedAt: any;
  menteesLimit: number;
  name: string;
  startedAt: any;
  tags?: Array<string>;
};

export type ExperienceLevelEnum =
  | 'ADVANCED'
  | 'BEGINNER'
  | 'EXPERT'
  | 'INTERMEDIATE';

export type ProgramStatusEnum =
  | 'COMPLETED'
  | 'DRAFT'
  | 'PUBLISHED';

export type UpdateProgramInput = {
  adminLogins?: Array<string> | null | undefined;
  description: string;
  domains?: Array<string> | null | undefined;
  endedAt: any;
  key: string;
  menteesLimit: number;
  name: string;
  startedAt: any;
  status: ProgramStatusEnum;
  tags?: Array<string> | null | undefined;
};

export type UpdateProgramStatusInput = {
  key: string;
  name: string;
  status: ProgramStatusEnum;
};

export type UpdateProgramMutationVariables = Exact<{
  input: Types.UpdateProgramInput;
}>;


export type UpdateProgramMutation = { updateProgram: { __typename: 'ProgramNode', description: string, domains: Array<string> | null, endedAt: any, experienceLevels: Array<Types.ExperienceLevelEnum> | null, id: string, key: string, menteesLimit: number | null, name: string, startedAt: any, status: Types.ProgramStatusEnum, tags: Array<string> | null, admins: Array<{ __typename: 'AdminNode', avatarUrl: string, id: string, login: string, name: string }> | null } };

export type CreateProgramMutationVariables = Exact<{
  input: Types.CreateProgramInput;
}>;


export type CreateProgramMutation = { createProgram: { __typename: 'ProgramNode', description: string, domains: Array<string> | null, endedAt: any, experienceLevels: Array<Types.ExperienceLevelEnum> | null, id: string, key: string, menteesLimit: number | null, name: string, startedAt: any, tags: Array<string> | null, admins: Array<{ __typename: 'AdminNode', avatarUrl: string, login: string, name: string }> | null } };

export type UpdateProgramStatusMutationVariables = Exact<{
  inputData: Types.UpdateProgramStatusInput;
}>;


export type UpdateProgramStatusMutation = { updateProgramStatus: { __typename: 'ProgramNode', id: string, key: string, status: Types.ProgramStatusEnum } };


export const UpdateProgramDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateProgram"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateProgramInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateProgram"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"domains"}},{"kind":"Field","name":{"kind":"Name","value":"endedAt"}},{"kind":"Field","name":{"kind":"Name","value":"experienceLevels"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"menteesLimit"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"startedAt"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"tags"}},{"kind":"Field","name":{"kind":"Name","value":"admins"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"avatarUrl"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"login"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]}}]} as unknown as DocumentNode<UpdateProgramMutation, UpdateProgramMutationVariables>;
export const CreateProgramDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateProgram"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateProgramInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createProgram"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"domains"}},{"kind":"Field","name":{"kind":"Name","value":"endedAt"}},{"kind":"Field","name":{"kind":"Name","value":"experienceLevels"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"menteesLimit"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"startedAt"}},{"kind":"Field","name":{"kind":"Name","value":"tags"}},{"kind":"Field","name":{"kind":"Name","value":"admins"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"avatarUrl"}},{"kind":"Field","name":{"kind":"Name","value":"login"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]}}]} as unknown as DocumentNode<CreateProgramMutation, CreateProgramMutationVariables>;
export const UpdateProgramStatusDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"updateProgramStatus"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"inputData"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateProgramStatusInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateProgramStatus"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"inputData"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}}]}}]} as unknown as DocumentNode<UpdateProgramStatusMutation, UpdateProgramStatusMutationVariables>;