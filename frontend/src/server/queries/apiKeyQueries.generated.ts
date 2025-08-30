import * as Types from '../../types/__generated__/graphql';

export type GetApiKeysQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type GetApiKeysQuery = { activeApiKeyCount: number, apiKeys: Array<{ __typename: 'ApiKeyNode', createdAt: unknown, expiresAt: unknown, isRevoked: boolean, name: string, uuid: unknown }> };

export type CreateApiKeyMutationVariables = Types.Exact<{
  name: Types.Scalars['String']['input'];
  expiresAt: Types.Scalars['DateTime']['input'];
}>;


export type CreateApiKeyMutation = { createApiKey: { __typename: 'CreateApiKeyResult', code: string | null, message: string | null, ok: boolean, rawKey: string | null, apiKey: { __typename: 'ApiKeyNode', createdAt: unknown, expiresAt: unknown, isRevoked: boolean, name: string, uuid: unknown } | null } };

export type RevokeApiKeyMutationVariables = Types.Exact<{
  uuid: Types.Scalars['UUID']['input'];
}>;


export type RevokeApiKeyMutation = { revokeApiKey: { __typename: 'RevokeApiKeyResult', code: string | null, message: string | null, ok: boolean } };
