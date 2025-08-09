export const mockDashboardCookies = async (page, mockDashboardData, isOwaspStaff) => {
  await page.route('**/api/auth/session', async (route) => {
    await route.fulfill({
      status: 200,
      json: {
        accessToken: 'test-access-token',
        expires: '2125-08-28T01:33:56.550Z',
        user: {
          isOwaspStaff: isOwaspStaff,
          login: 'testuser',
        },
      },
    })
  })
  await page.route('**/graphql/', async (route, request) => {
    const postData = request.postDataJSON()
    switch (postData.operationName) {
      case 'SyncDjangoSession':
        await route.fulfill({
          status: 200,
          json: {
            data: {
              githubAuth: {
                message: 'test message',
                ok: true,
                user: { isOwaspStaff: isOwaspStaff },
              },
            },
          },
        })
        break
      default:
        await route.fulfill({
          status: 200,
          json: {
            data: mockDashboardData,
          },
        })
        break
    }
  })
  await page.context().addCookies([
    {
      name: 'csrftoken',
      value: 'abc123',
      domain: 'localhost',
      path: '/',
    },
    {
      name: 'nest.session-id',
      value: 'test-session-id',
      domain: 'localhost',
      path: '/',
    },
    {
      name: 'next-auth.csrf-token',
      value: 'test-csrf-token',
      domain: 'localhost',
      path: '/',
    },
    {
      name: 'next-auth.callback-url',
      value: '/',
      domain: 'localhost',
      path: '/',
    },
    {
      name: 'next-auth.session-token',
      value: 'test-session-token',
      domain: 'localhost',
      path: '/',
    },
  ])
}
