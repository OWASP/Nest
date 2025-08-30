import * as Types from '../../types/__generated__/graphql';

export type IsProjectLeaderQueryVariables = Types.Exact<{
  login: Types.Scalars['String']['input'];
}>;


export type IsProjectLeaderQuery = { isProjectLeader: boolean };

export type IsMentorQueryVariables = Types.Exact<{
  login: Types.Scalars['String']['input'];
}>;


export type IsMentorQuery = { isMentor: boolean };
