import { test, expect, Page, BrowserContext } from '@playwright/test'

test.describe.serial('Project Details Page', () => {
  let page: Page
  let context: BrowserContext

  test.beforeAll(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      baseURL: testInfo.project.use.baseURL,
    })
    page = await context.newPage()
    await page.goto('/projects/nest', { timeout: 25000 })
  })
  test.afterAll(async () => {
    await context.close()
  })

  test('should have a heading', async () => {
    await expect(page.getByRole('heading', { name: 'OWASP Nest', exact: true })).toBeVisible()
    await expect(
      page.getByText(
        'OWASP Nest is a code project aimed at improving how OWASP manages its collection of projects. It will create a more organized system with better navigation and user experience while keeping the current risk profile intact. The project plans to use the Github API to keep track of project updates and automate certain tasks. Project leaders will be able to add important information using standardized files. The goal is to have a minimum viable product ready by September 2024, with hopes of completing it by the end of the year.'
      )
    ).toBeVisible()
  })

  test('should have project details block', async () => {
    await expect(page.getByRole('heading', { name: 'Project Details' })).toBeVisible()
    await expect(page.getByText('Level: Lab')).toBeVisible()
    await expect(page.getByText('Type: Code')).toBeVisible()
    await expect(
      page.getByText('Leaders: Arkadii Yakovets, Kate Golovanova, Starr Brown')
    ).toBeVisible()
    await expect(page.getByText('URL: https://owasp.org/www-project-nest')).toBeVisible()
  })

  test('should have project statistics block', async () => {
    await expect(page.getByText('Stars').first()).toBeVisible()
    await expect(page.getByText('Forks').first()).toBeVisible()
    await expect(page.getByText('Contributors').first()).toBeVisible()
    await expect(page.getByText('Issues').first()).toBeVisible()
    await expect(page.getByText('Repositories').first()).toBeVisible()
  })

  test('should have project topics', async () => {
    await expect(page.getByRole('heading', { name: 'Topics' })).toBeVisible()
    await expect(page.getByText('graphql', { exact: true })).toBeVisible()
    await expect(page.getByText('django', { exact: true })).toBeVisible()
    await expect(page.getByText('python', { exact: true })).toBeVisible()
    await expect(page.getByText('nextjs', { exact: true })).toBeVisible()
  })

  test('should have project languages', async () => {
    await expect(page.getByRole('heading', { name: 'Languages' })).toBeVisible()
    await expect(page.getByText('Python', { exact: true })).toBeVisible()
    await expect(page.getByText('TypeScript', { exact: true })).toBeVisible()
  })

  test('should have top contributors', async () => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(page.getByText('Arkadii Yakovets', { exact: true }).first()).toBeVisible()
    await expect(page.getByText('Kate Golovanova', { exact: true }).first()).toBeVisible()
    await expect(page.getByText('Ahmed Gouda', { exact: true })).toBeVisible()
  })

  test('toggle top contributors', async () => {
    await expect(page.getByRole('button', { name: 'Show more' }).last()).toBeVisible()
    await page.getByRole('button', { name: 'Show more' }).last().click()
    await expect(page.getByRole('button', { name: 'Show less' })).toBeVisible()
    await page.getByRole('button', { name: 'Show less' }).click()
    await expect(page.getByRole('button', { name: 'Show more' }).last()).toBeVisible()
  })

  test('should have project recent issues', async () => {
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    await expect(page.getByText('Nest').first()).toBeVisible()
  })

  test('should have project recent releases', async () => {
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
  })

  test('should have project recent milestones', async () => {
    await expect(page.getByRole('heading', { name: 'Recent Milestones' })).toBeVisible()
  })

  test('should display recent pull requests section', async () => {
    await expect(page.getByRole('heading', { name: 'Recent Pull Requests' })).toBeVisible()
    await expect(page.getByText('Nest').first()).toBeVisible()
  })

  test('should display health metrics section', async () => {
    await expect(page.getByText('Issues Trend')).toBeVisible()
    await expect(page.getByText('Pull Requests Trend')).toBeVisible()
    await expect(page.getByText('Stars Trend')).toBeVisible()
    await expect(page.getByText('Forks Trend')).toBeVisible()
    await expect(page.getByText('Days Since Last Commit and Release')).toBeVisible()
  })

  test('should have project repositories', async () => {
    await expect(page.getByRole('heading', { name: 'Repositories' })).toBeVisible()
    await expect(page.getByText('www-project-nest', { exact: true })).toBeVisible()
    await page.getByText('www-project-nest', { exact: true }).click()
    await expect(page).toHaveURL('organizations/OWASP/repositories/www-project-nest')
  })
})
