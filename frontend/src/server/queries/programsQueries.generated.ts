import * as Types from '../../types/__generated__/graphql';

export type GetMyProgramsQueryVariables = Types.Exact<{
  search?: Types.InputMaybe<Types.Scalars['String']['input']>;
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  limit?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type GetMyProgramsQuery = { myPrograms: { __typename: 'PaginatedPrograms', currentPage: number, totalPages: number, programs: Array<{ __typename: 'ProgramNode', id: string, key: string, name: string, description: string, startedAt: unknown, endedAt: unknown, userRole: string | null }> } };

export type GetProgramDetailsQueryVariables = Types.Exact<{
  programKey: Types.Scalars['String']['input'];
}>;


export type GetProgramDetailsQuery = { getProgram: { __typename: 'ProgramNode', id: string, key: string, name: string, description: string, status: Types.ProgramStatusEnum, menteesLimit: number | null, experienceLevels: Array<Types.ExperienceLevelEnum> | null, startedAt: unknown, endedAt: unknown, domains: Array<string> | null, tags: Array<string> | null, admins: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> | null } };

export type GetProgramAndModulesQueryVariables = Types.Exact<{
  programKey: Types.Scalars['String']['input'];
}>;


export type GetProgramAndModulesQuery = { getProgram: { __typename: 'ProgramNode', id: string, key: string, name: string, description: string, status: Types.ProgramStatusEnum, menteesLimit: number | null, experienceLevels: Array<Types.ExperienceLevelEnum> | null, startedAt: unknown, endedAt: unknown, domains: Array<string> | null, tags: Array<string> | null, admins: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> | null }, getProgramModules: Array<{ __typename: 'ModuleNode', id: string, key: string, name: string, description: string, experienceLevel: Types.ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, mentors: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> }> };

export type GetProgramAdminDetailsQueryVariables = Types.Exact<{
  programKey: Types.Scalars['String']['input'];
}>;


export type GetProgramAdminDetailsQuery = { getProgram: { __typename: 'ProgramNode', id: string, key: string, name: string, admins: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> | null } };
