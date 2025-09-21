import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type LeaderFieldsFragment = { __typename: 'UserNode', id: string, avatarUrl: string, company: string, location: string, login: string, name: string };

export const LeaderFieldsFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"LeaderFields"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"UserNode"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"avatarUrl"}},{"kind":"Field","name":{"kind":"Name","value":"company"}},{"kind":"Field","name":{"kind":"Name","value":"location"}},{"kind":"Field","name":{"kind":"Name","value":"login"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<LeaderFieldsFragment, unknown>;