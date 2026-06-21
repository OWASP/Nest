import { authCookies } from './mockAuthCookies'

export const mockClaimAuth = async (page, mockData, login = 'testuser', operationNames?: string[]) => {
  await page.route('**/api/auth/session', async (route) => {
    await route.fulfill({
      status: 200,
      json: {
        accessToken: 'test-access-token',
        expires: '2125-08-28T01:33:56.550Z',
        user: {
          isOwaspStaff: false,
          login,
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
              user: { isOwaspStaff: false },
            },
          },
        },
      })
    } else if (operationNames && !operationNames.includes(postData.operationName)) {
      await route.abort('blockedbyclient')
    } else {
      await route.fulfill({
        status: 200,
        json: { data: mockData },
      })
    }
  })
  await page.context().addCookies(authCookies)
}
