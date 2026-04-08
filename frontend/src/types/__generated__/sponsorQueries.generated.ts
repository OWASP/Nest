import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type GetSponsorsPageDataQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type GetSponsorsPageDataQuery = { sponsors: Array<{ __typename: 'SponsorNode', id: string, imageUrl: string, name: string, sponsorType: string, url: string }> };


export const GetSponsorsPageDataDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetSponsorsPageData"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"sponsors"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"imageUrl"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"sponsorType"}},{"kind":"Field","name":{"kind":"Name","value":"url"}}]}}]}}]} as unknown as DocumentNode<GetSponsorsPageDataQuery, GetSponsorsPageDataQueryVariables>;