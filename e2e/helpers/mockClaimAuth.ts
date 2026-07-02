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
    const headers = request.headers()
    const contentType = headers['content-type'] || ''
    let operationName: string | undefined

    if (contentType.includes('application/json')) {
      const postData = request.postDataJSON()
      operationName = postData.operationName
    } else {
      const body = (await request.body()).toString()
      const match = body.match(/"operationName"\s*:\s*"([^"]+)"/)
      operationName = match?.[1] ?? undefined
    }

    if (operationName === 'SyncDjangoSession') {
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
    } else if (operationNames && operationName && !operationNames.includes(operationName)) {
      await route.abort('aborted')
    } else {
      await route.fulfill({
        status: 200,
        json: { data: mockData },
      })
    }
  })
  await page.context().addCookies(authCookies)
}
