export const mockActiveSubscription = {
  mySnapshotSubscription: {
    id: '1',
    frequency: 'weekly',
    isActive: true,
    includeChapters: true,
    includeEvents: true,
    includeIssues: true,
    includePosts: true,
    includeProjects: true,
    includePullRequests: true,
    includeReleases: true,
    includeUsers: true,
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-06-01T00:00:00Z',
  },
}

export const mockInactiveSubscription = {
  mySnapshotSubscription: {
    id: '2',
    frequency: 'monthly',
    isActive: false,
    includeChapters: true,
    includeEvents: true,
    includeIssues: true,
    includePosts: true,
    includeProjects: true,
    includePullRequests: true,
    includeReleases: true,
    includeUsers: true,
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-06-01T00:00:00Z',
  },
}

export const mockNoSubscription = {
  mySnapshotSubscription: null,
}

export const mockCreateSubscriptionResult = {
  data: {
    createSnapshotSubscription: {
      ok: true,
      message: 'Subscription created successfully.',
      subscription: mockActiveSubscription.mySnapshotSubscription,
    },
  },
}

export const mockUpdateSubscriptionResult = {
  data: {
    updateSnapshotSubscription: {
      ok: true,
      message: 'Subscription updated successfully.',
      subscription: mockActiveSubscription.mySnapshotSubscription,
    },
  },
}

export const mockCancelSubscriptionResult = {
  data: {
    cancelSnapshotSubscription: {
      ok: true,
      message: 'Subscription cancelled successfully.',
      subscription: { ...mockActiveSubscription.mySnapshotSubscription, isActive: false },
    },
  },
}

export const mockEntitySubscriptions = {
  myEntitySubscriptions: [
    {
      id: '10',
      frequency: 'weekly',
      isActive: true,
      chapter: null,
      committee: null,
      project: { id: '1', name: 'OWASP Nest' },
      includeIssues: true,
      includePullRequests: true,
      includeReleases: false,
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-06-01T00:00:00Z',
    },
    {
      id: '12',
      frequency: 'weekly',
      isActive: true,
      chapter: { id: '2', name: 'OWASP Aarhus' },
      committee: null,
      project: null,
      includeIssues: true,
      includePullRequests: false,
      includeReleases: false,
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-06-01T00:00:00Z',
    },
  ],
}

export const mockInactiveEntitySubscriptions = {
  myEntitySubscriptions: [
    {
      id: '11',
      frequency: 'monthly',
      isActive: false,
      chapter: null,
      committee: null,
      project: { id: '3', name: 'OWASP ZAP' },
      includeIssues: true,
      includePullRequests: true,
      includeReleases: true,
      createdAt: '2025-02-01T00:00:00Z',
      updatedAt: '2025-06-01T00:00:00Z',
    },
  ],
}

export const mockNoEntitySubscriptions = {
  myEntitySubscriptions: [],
}

export const mockCancelEntitySubscriptionResult = {
  data: {
    cancelEntitySubscription: {
      ok: true,
      message: 'Subscription cancelled successfully.',
      subscription: { id: '10', isActive: false },
    },
  },
}

export const mockDeleteEntitySubscriptionResult = {
  data: {
    deleteEntitySubscription: {
      ok: true,
      message: 'Subscription deleted successfully.',
    },
  },
}

export const mockReactivateEntitySubscriptionResult = {
  data: {
    reactivateEntitySubscription: {
      ok: true,
      message: 'Subscription reactivated successfully.',
      subscription: { id: '11', isActive: true },
    },
  },
}

export const mockCreateEntitySubscriptionResult = {
  data: {
    createEntitySubscription: {
      ok: true,
      message: 'Entity subscription created successfully.',
      subscription: mockEntitySubscriptions.myEntitySubscriptions[0],
    },
  },
}

export const mockUpdateEntitySubscriptionResult = {
  data: {
    updateEntitySubscription: {
      ok: true,
      message: 'Entity subscription updated successfully.',
      subscription: mockEntitySubscriptions.myEntitySubscriptions[0],
    },
  },
}
