/** Internal type. DO NOT USE DIRECTLY. */
type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
/** Internal type. DO NOT USE DIRECTLY. */
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type CreateModuleInput = {
  description: string;
  domains?: Array<string>;
  endedAt: any;
  experienceLevel: ExperienceLevelEnum;
  labels?: Array<string>;
  mentorLogins?: Array<string> | null | undefined;
  name: string;
  programKey: string;
  projectId: string | number;
  projectName: string;
  startedAt: any;
  tags?: Array<string>;
};

export type ExperienceLevelEnum =
  | 'ADVANCED'
  | 'BEGINNER'
  | 'EXPERT'
  | 'INTERMEDIATE';

export type ReorderModulesInput = {
  moduleKeys: Array<string>;
  programKey: string;
};

export type UpdateModuleInput = {
  description: string;
  domains?: Array<string>;
  endedAt: any;
  experienceLevel: ExperienceLevelEnum;
  key: string;
  labels?: Array<string>;
  mentorLogins?: Array<string> | null | undefined;
  name: string;
  programKey: string;
  projectId: string | number;
  projectName: string;
  startedAt: any;
  tags?: Array<string>;
};

export type UpdateModuleMutationVariables = Exact<{
  input: Types.UpdateModuleInput;
}>;


export type UpdateModuleMutation = { updateModule: { __typename: 'ModuleNode', id: string, key: string, name: string, description: string, experienceLevel: Types.ExperienceLevelEnum, startedAt: any, endedAt: any, tags: Array<string> | null, domains: Array<string> | null, labels: Array<string> | null, projectId: string | null, mentors: Array<{ __typename: 'MentorNode', id: string, login: string, name: string, avatarUrl: string }>, mentees: Array<{ __typename: 'UserNode', id: string, login: string, name: string, avatarUrl: string }> } };

export type CreateModuleMutationVariables = Exact<{
  input: Types.CreateModuleInput;
}>;


export type CreateModuleMutation = { createModule: { __typename: 'ModuleNode', description: string, domains: Array<string> | null, endedAt: any, experienceLevel: Types.ExperienceLevelEnum, id: string, key: string, labels: Array<string> | null, name: string, projectId: string | null, startedAt: any, tags: Array<string> | null, mentors: Array<{ __typename: 'MentorNode', avatarUrl: string, id: string, login: string, name: string }>, mentees: Array<{ __typename: 'UserNode', avatarUrl: string, id: string, login: string, name: string }> } };

export type ReorderModulesMutationVariables = Exact<{
  input: Types.ReorderModulesInput;
}>;


export type ReorderModulesMutation = { reorderModules: Array<{ __typename: 'ModuleNode', id: string, key: string, name: string, order: number }> };


export const UpdateModuleDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateModule"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateModuleInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateModule"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"experienceLevel"}},{"kind":"Field","name":{"kind":"Name","value":"startedAt"}},{"kind":"Field","name":{"kind":"Name","value":"endedAt"}},{"kind":"Field","name":{"kind":"Name","value":"tags"}},{"kind":"Field","name":{"kind":"Name","value":"domains"}},{"kind":"Field","name":{"kind":"Name","value":"labels"}},{"kind":"Field","name":{"kind":"Name","value":"projectId"}},{"kind":"Field","name":{"kind":"Name","value":"mentors"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"login"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"avatarUrl"}}]}},{"kind":"Field","name":{"kind":"Name","value":"mentees"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"login"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"avatarUrl"}}]}}]}}]}}]} as unknown as DocumentNode<UpdateModuleMutation, UpdateModuleMutationVariables>;
export const CreateModuleDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateModule"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateModuleInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createModule"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"domains"}},{"kind":"Field","name":{"kind":"Name","value":"endedAt"}},{"kind":"Field","name":{"kind":"Name","value":"experienceLevel"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"labels"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"projectId"}},{"kind":"Field","name":{"kind":"Name","value":"startedAt"}},{"kind":"Field","name":{"kind":"Name","value":"tags"}},{"kind":"Field","name":{"kind":"Name","value":"mentors"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"avatarUrl"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"login"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"mentees"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"avatarUrl"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"login"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]}}]} as unknown as DocumentNode<CreateModuleMutation, CreateModuleMutationVariables>;
export const ReorderModulesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"ReorderModules"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ReorderModulesInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"reorderModules"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"inputData"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"order"}}]}}]}}]} as unknown as DocumentNode<ReorderModulesMutation, ReorderModulesMutationVariables>;