export const mockActiveSubscription = {
  mySubscription: {
    id: '1',
    frequency: 'weekly',
    isActive: true,
    includeChapters: true,
    includeEvents: true,
    includePosts: true,
    includeUsers: true,
    projectPreferences: [
      {
        id: '10',
        project: { id: '100', name: 'OWASP Nest' },
        includeIssues: true,
        includePullRequests: true,
        includeReleases: false,
      },
    ],
    chapters: [{ id: '200', name: 'OWASP Aarhus' }],
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-06-01T00:00:00Z',
  },
}

export const mockInactiveSubscription = {
  mySubscription: {
    id: '2',
    frequency: 'monthly',
    isActive: false,
    includeChapters: true,
    includeEvents: true,
    includePosts: true,
    includeUsers: true,
    projectPreferences: [],
    chapters: [],
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-06-01T00:00:00Z',
  },
}

export const mockNoSubscription = {
  mySubscription: null,
}

export const mockCreateSubscriptionResult = {
  data: {
    createSnapshotSubscription: {
      ok: true,
      message: 'Subscription created successfully.',
      subscription: mockActiveSubscription.mySubscription,
    },
  },
}

export const mockUpdateSubscriptionResult = {
  data: {
    updateSnapshotSubscription: {
      ok: true,
      message: 'Subscription updated successfully.',
      subscription: mockActiveSubscription.mySubscription,
    },
  },
}

export const mockCancelSubscriptionResult = {
  data: {
    cancelSnapshotSubscription: {
      ok: true,
      message: 'Subscription cancelled successfully.',
      subscription: { ...mockActiveSubscription.mySubscription, isActive: false },
    },
  },
}
