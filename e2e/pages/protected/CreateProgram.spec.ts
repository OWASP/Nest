import { loginAsPage } from '@e2e/helpers/loginAs'
import { expect, test } from '@playwright/test'

const USER = 'e2e-user'

test.describe('Create Program', () => {
  test('leader creates a program and opens its details page', async ({ page }, testInfo) => {
    test.setTimeout(60_000)

    const programName = `E2E ${testInfo.project.name} ${Date.now()}`

    await loginAsPage(page, USER)
    await page.goto('/my/mentorship', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { name: 'My Mentorship' })).toBeVisible()
    await page.getByRole('button', { name: 'Create Program' }).click()

    await expect(page).toHaveURL(/\/my\/mentorship\/programs\/create/)
    await expect(page.getByRole('heading', { name: 'Create Program' })).toBeVisible()

    await page.locator('#program-name').fill(programName)
    await page.locator('#program-description').fill('E2E presentation program')
    await page.locator('#program-start-date').fill('2030-01-01')
    await page.locator('#program-end-date').fill('2030-12-31')
    await page.getByRole('button', { name: 'Save' }).click()

    await expect(page).toHaveURL(/\/my\/mentorship\/?$/)
    const programHeading = page.getByRole('heading', { name: programName })
    await expect(programHeading).toBeVisible()
    await programHeading.click()

    await expect(page).toHaveURL(/\/my\/mentorship\/programs\/[^/]+/)
    await expect(page.getByRole('heading', { level: 1, name: programName })).toBeVisible()
  })
})
