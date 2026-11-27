/** Internal type. DO NOT USE DIRECTLY. */
type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
/** Internal type. DO NOT USE DIRECTLY. */
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type DeleteModuleMutationVariables = Exact<{
  programKey: string;
  moduleKey: string;
}>;


export type DeleteModuleMutation = { deleteModule: string };


export const DeleteModuleDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteModule"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"programKey"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"moduleKey"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteModule"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"programKey"},"value":{"kind":"Variable","name":{"kind":"Name","value":"programKey"}}},{"kind":"Argument","name":{"kind":"Name","value":"moduleKey"},"value":{"kind":"Variable","name":{"kind":"Name","value":"moduleKey"}}}]}]}}]} as unknown as DocumentNode<DeleteModuleMutation, DeleteModuleMutationVariables>;