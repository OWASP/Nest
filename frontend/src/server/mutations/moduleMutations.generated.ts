import * as Types from '../../types/__generated__/graphql';

export type UpdateModuleMutationVariables = Types.Exact<{
  input: Types.UpdateModuleInput;
}>;


export type UpdateModuleMutation = { updateModule: { __typename: 'ModuleNode', id: string, key: string, name: string, description: string, experienceLevel: Types.ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, tags: Array<string> | null, domains: Array<string> | null, projectId: string | null, mentors: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> } };

export type CreateModuleMutationVariables = Types.Exact<{
  input: Types.CreateModuleInput;
}>;


export type CreateModuleMutation = { createModule: { __typename: 'ModuleNode', id: string, key: string, name: string, description: string, experienceLevel: Types.ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, domains: Array<string> | null, tags: Array<string> | null, projectId: string | null, mentors: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> } };
