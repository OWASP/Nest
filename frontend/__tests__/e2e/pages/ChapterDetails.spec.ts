import { test, expect, Page } from '@playwright/test'

test.describe('Chapter Details Page', () => {
  let page: Page
  test.beforeAll(async ({ browser }) => {
    const context = await browser.newContext()
    page = await context.newPage()
    await page.goto('/chapters/rosario', { timeout: 25000 })
  })
  test.afterAll(async () => {
    await page.close()
  })

  test('should have a heading and summary', async () => {
    await expect(page.getByRole('heading', { name: 'OWASP Rosario', exact: true })).toBeVisible()
    await expect(
      page.getByText(
        'The OWASP Rosario chapter is located in Argentina, South America. It is a part of the OWASP community, which focuses on improving software security. The chapter encourages local members to participate in various projects, events, and discussions related to application security. Although the exact age and size of the chapter are not specified, it is part of a larger organization that welcomes everyone interested in learning about software security. Members can also become involved by attending meetups, contributing to projects, and networking with others. The chapter promotes diversity and aims to create a supportive environment for all participants. Overall, it provides a platform for individuals to enhance their knowledge and reputation in the field of application security.'
      )
    ).toBeVisible()
  })

  test('should have chapter details block', async () => {
    await expect(page.getByText('Location: Test City, Test')).toBeVisible()
    await expect(page.getByText('Region: Test Region')).toBeVisible()
    await expect(page.getByRole('link', { name: 'https://owasp.org/test-chapter' })).toBeVisible()
  })

  test('should have map with geolocation', async () => {
    const unlockButton = page.getByRole('button', { name: 'Unlock map' })
    await expect(unlockButton).toBeVisible()

    await unlockButton.click()

    await expect(page.getByRole('button', { name: 'Zoom in' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Zoom out' })).toBeVisible()

    const marker = page.locator('.leaflet-marker-icon').first()
    await marker.click()

    const popupButton = page.getByRole('button', { name: 'OWASP Test Chapter' })
    await expect(popupButton).toBeVisible()
  })

  test('should have top contributors', async () => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(
      page.getByRole('img', { name: "Contributor 1's avatar", exact: true })
    ).toBeVisible()
    await expect(page.getByText('Contributor 1', { exact: true })).toBeVisible()
    await expect(
      page.getByRole('img', { name: "Contributor 2's avatar", exact: true })
    ).toBeVisible()
    await expect(page.getByText('Contributor 2', { exact: true })).toBeVisible()
  })

  test('toggle top contributors', async () => {
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
    await page.getByRole('button', { name: 'Show more' }).click()
    await expect(page.getByRole('button', { name: 'Show less' })).toBeVisible()
    await page.getByRole('button', { name: 'Show less' }).click()
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
  })

  test('should have leaders block', async () => {
    await expect(page.getByRole('heading', { name: 'Leaders' })).toBeVisible()
    await expect(page.getByText('Bob')).toBeVisible()
    await expect(page.getByText('Chapter Leader')).toBeVisible()
  })
})
