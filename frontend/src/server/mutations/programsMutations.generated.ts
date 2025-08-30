import * as Types from '../../types/__generated__/graphql';

export type UpdateProgramMutationVariables = Types.Exact<{
  input: Types.UpdateProgramInput;
}>;


export type UpdateProgramMutation = { updateProgram: { __typename: 'ProgramNode', key: string, name: string, description: string, status: Types.ProgramStatusEnum, menteesLimit: number | null, startedAt: unknown, endedAt: unknown, tags: Array<string> | null, domains: Array<string> | null, admins: Array<{ __typename: 'MentorNode', login: string }> | null } };

export type CreateProgramMutationVariables = Types.Exact<{
  input: Types.CreateProgramInput;
}>;


export type CreateProgramMutation = { createProgram: { __typename: 'ProgramNode', id: string, key: string, name: string, description: string, menteesLimit: number | null, startedAt: unknown, endedAt: unknown, tags: Array<string> | null, domains: Array<string> | null, admins: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> | null } };

export type UpdateProgramStatusMutationVariables = Types.Exact<{
  inputData: Types.UpdateProgramStatusInput;
}>;


export type UpdateProgramStatusMutation = { updateProgramStatus: { __typename: 'ProgramNode', key: string, status: Types.ProgramStatusEnum } };
