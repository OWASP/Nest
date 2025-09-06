import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type IsProjectLeaderQueryVariables = Types.Exact<{
  login: Types.Scalars['String']['input'];
}>;


export type IsProjectLeaderQuery = { isProjectLeader: boolean };

export type IsMentorQueryVariables = Types.Exact<{
  login: Types.Scalars['String']['input'];
}>;


export type IsMentorQuery = { isMentor: boolean };


export const IsProjectLeaderDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"IsProjectLeader"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"login"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isProjectLeader"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"login"},"value":{"kind":"Variable","name":{"kind":"Name","value":"login"}}}]}]}}]} as unknown as DocumentNode<IsProjectLeaderQuery, IsProjectLeaderQueryVariables>;
export const IsMentorDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"IsMentor"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"login"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isMentor"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"login"},"value":{"kind":"Variable","name":{"kind":"Name","value":"login"}}}]}]}}]} as unknown as DocumentNode<IsMentorQuery, IsMentorQueryVariables>;