export const mockApolloClient = {
  query: async () => ({
    data: {
      chapter: null,
      project: null,
      committee: null,
      organization: null,
      snapshot: null,
      user: null,
      repository: null,
    },
  }),
}
