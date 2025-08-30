import * as Types from '../../types/__generated__/graphql';

export type GetModulesByProgramQueryVariables = Types.Exact<{
  programKey: Types.Scalars['String']['input'];
}>;


export type GetModulesByProgramQuery = { getProgramModules: Array<{ __typename: 'ModuleNode', id: string, key: string, name: string, description: string, experienceLevel: Types.ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, projectId: string | null, projectName: string | null, mentors: Array<{ __typename: 'MentorNode', id: string, login: string, avatarUrl: string }> }> };

export type GetModuleByIdQueryVariables = Types.Exact<{
  moduleKey: Types.Scalars['String']['input'];
  programKey: Types.Scalars['String']['input'];
}>;


export type GetModuleByIdQuery = { getModule: { __typename: 'ModuleNode', id: string, key: string, name: string, description: string, tags: Array<string> | null, domains: Array<string> | null, experienceLevel: Types.ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, mentors: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> } };

export type GetProgramAdminsAndModulesQueryVariables = Types.Exact<{
  programKey: Types.Scalars['String']['input'];
  moduleKey: Types.Scalars['String']['input'];
}>;


export type GetProgramAdminsAndModulesQuery = { getProgram: { __typename: 'ProgramNode', id: string, admins: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> | null }, getModule: { __typename: 'ModuleNode', id: string, key: string, name: string, description: string, tags: Array<string> | null, projectId: string | null, projectName: string | null, domains: Array<string> | null, experienceLevel: Types.ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, mentors: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> } };
