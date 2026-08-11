const baseSubscription = {
  includeChapters: true,
  includeEvents: true,
  includeIssues: true,
  includePosts: true,
  includeProjects: true,
  includePullRequests: true,
  includeReleases: true,
  includeUsers: true,
  subscribedProjects: [] as { id: number; name: string }[],
  subscribedChapters: [] as { id: number; name: string }[],
  subscribedCommittees: [] as { id: number; name: string }[],
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-06-01T00:00:00Z',
}

export const mockActiveSubscriptions = {
  mySnapshotSubscriptions: [
    {
      ...baseSubscription,
      id: '1',
      name: 'My Weekly Digest',
      frequency: 'weekly',
      isActive: true,
      subscribedProjects: [{ id: 1, name: 'OWASP Nest' }],
      subscribedChapters: [{ id: 2, name: 'OWASP Aarhus' }],
    },
  ],
}

export const mockMultipleSubscriptions = {
  mySnapshotSubscriptions: [
    {
      ...baseSubscription,
      id: '1',
      name: 'My Weekly Digest',
      frequency: 'weekly',
      isActive: true,
      subscribedProjects: [{ id: 1, name: 'OWASP Nest' }],
    },
    {
      ...baseSubscription,
      id: '2',
      name: 'Monthly Security',
      frequency: 'monthly',
      isActive: true,
    },
  ],
}

export const mockNoSubscriptions = {
  mySnapshotSubscriptions: [],
}

export const mockCreateSubscriptionResult = {
  data: {
    createSnapshotSubscription: {
      ok: true,
      message: 'Subscription created successfully.',
      subscription: mockActiveSubscriptions.mySnapshotSubscriptions[0],
    },
  },
}

export const mockUpdateSubscriptionResult = {
  data: {
    updateSnapshotSubscription: {
      ok: true,
      message: 'Subscription updated successfully.',
      subscription: mockActiveSubscriptions.mySnapshotSubscriptions[0],
    },
  },
}

export const mockDeleteSubscriptionResult = {
  data: {
    deleteSnapshotSubscription: {
      ok: true,
      message: 'Subscription deleted successfully.',
    },
  },
}
