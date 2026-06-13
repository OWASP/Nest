/** Internal type. DO NOT USE DIRECTLY. */
type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
/** Internal type. DO NOT USE DIRECTLY. */
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type GetApiKeysQueryVariables = Exact<{ [key: string]: never; }>;


export type GetApiKeysQuery = { activeApiKeyCount: number, apiKeys: Array<{ __typename: 'ApiKeyNode', id: string, createdAt: any, expiresAt: any, isRevoked: boolean, name: string, uuid: any }> };

export type CreateApiKeyMutationVariables = Exact<{
  name: string;
  expiresAt: any;
}>;


export type CreateApiKeyMutation = { createApiKey: { __typename: 'CreateApiKeyResult', code: string | null, message: string | null, ok: boolean, rawKey: string | null, apiKey: { __typename: 'ApiKeyNode', id: string, createdAt: any, expiresAt: any, isRevoked: boolean, name: string, uuid: any } | null } };

export type RevokeApiKeyMutationVariables = Exact<{
  uuid: any;
}>;


export type RevokeApiKeyMutation = { revokeApiKey: { __typename: 'RevokeApiKeyResult', code: string | null, message: string | null, ok: boolean } };


export const GetApiKeysDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetApiKeys"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"activeApiKeyCount"}},{"kind":"Field","name":{"kind":"Name","value":"apiKeys"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"expiresAt"}},{"kind":"Field","name":{"kind":"Name","value":"isRevoked"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"uuid"}}]}}]}}]} as unknown as DocumentNode<GetApiKeysQuery, GetApiKeysQueryVariables>;
export const CreateApiKeyDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateApiKey"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"name"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"expiresAt"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DateTime"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createApiKey"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"name"},"value":{"kind":"Variable","name":{"kind":"Name","value":"name"}}},{"kind":"Argument","name":{"kind":"Name","value":"expiresAt"},"value":{"kind":"Variable","name":{"kind":"Name","value":"expiresAt"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"apiKey"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"expiresAt"}},{"kind":"Field","name":{"kind":"Name","value":"isRevoked"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"uuid"}}]}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"rawKey"}}]}}]}}]} as unknown as DocumentNode<CreateApiKeyMutation, CreateApiKeyMutationVariables>;
export const RevokeApiKeyDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"RevokeApiKey"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"uuid"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"revokeApiKey"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"uuid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"uuid"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"ok"}}]}}]}}]} as unknown as DocumentNode<RevokeApiKeyMutation, RevokeApiKeyMutationVariables>;