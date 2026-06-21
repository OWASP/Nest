import { authCookies } from './mockAuthCookies'

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
    if (postData.operationName === 'SyncDjangoSession') {
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
    } else {
      await route.fulfill({
        status: 200,
        json: {
          data: mockDashboardData,
        },
      })
    }
  })
  await page.context().addCookies(authCookies)
}
