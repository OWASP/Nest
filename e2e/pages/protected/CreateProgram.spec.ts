import { loginAsPage } from '@e2e/helpers/loginAs'
import { expect, Page, test } from '@playwright/test'

const USER = 'e2e-user'

async function createProgram(page: Page, name: string) {
  const csrfResponse = await page.request.get('/csrf/')
  const { csrftoken } = await csrfResponse.json()
  const body = await (
    await page.request.post('/graphql/', {
      data: {
        query: `mutation ($input: CreateProgramInput!) {
          createProgram(inputData: $input) { key name }
        }`,
        variables: {
          input: {
            description: 'E2E program',
            domains: [],
            endedAt: '2030-12-31T00:00:00.000Z',
            menteesLimit: 0,
            name,
            startedAt: '2030-01-01T00:00:00.000Z',
            tags: [],
          },
        },
      },
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
    })
  ).json()
  if (body.errors || !body.data?.createProgram?.key) {
    throw new Error(`createProgram failed: ${JSON.stringify(body)}`)
  }
  return body.data.createProgram as { key: string; name: string }
}

test.describe('Create Program', () => {
  test('leader creates a program and opens its details page', async ({ page }, testInfo) => {
    const programName = `E2E ${testInfo.project.name} ${Date.now()}`

    await loginAsPage(page, USER)
    await page.goto('/my/mentorship', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { name: 'My Mentorship' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Create Program' })).toBeVisible()

    const program = await createProgram(page, programName)

    await page.goto('/my/mentorship', { waitUntil: 'domcontentloaded' })
    await page.getByRole('heading', { name: program.name }).click()
    await expect(page).toHaveURL(`/my/mentorship/programs/${program.key}`)
    await expect(page.getByRole('heading', { level: 1, name: program.name })).toBeVisible()
  })
})
