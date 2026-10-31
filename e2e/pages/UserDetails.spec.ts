import { test, expect } from '@playwright/test'

test.describe('User Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/members/arkid15r', { waitUntil: 'domcontentloaded' })
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Arkadii Yakovets', exact: true })).toBeVisible()
    await expect(page.getByText('@arkid15r')).toBeVisible()
  })

  test('should have user details block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'User Details' })).toBeVisible()
    await expect(page.getByText(/Location:/i)).toBeVisible()
    await expect(page.getByText(/Email:/i)).toBeVisible()
  })

  test('should have user stats block', async ({ page }) => {
    const stats = ['Followers', 'Following', 'Repositories']
    for (const stat of stats) {
      const text = String.raw`\d.*${stat}`
      await expect(
        page
          .locator('div')
          .filter({ hasText: new RegExp(text) })
          .first()
      ).toBeVisible()
    }
  })

  test('keeps contribution cells square when the viewport or theme changes', async ({ page }) => {
    const cells = page.locator('.contribution-heatmap .apexcharts-heatmap-rect[val]')

    for (const width of [390, 768, 1280]) {
      await page.setViewportSize({ width, height: 900 })
      await expect(cells.first()).toBeVisible()
      for (const change of [1, 2]) {
        const toggle = page.getByRole('button', { name: /^Enable (light|dark) mode$/ })
        const requestedTheme = await toggle.getAttribute('aria-label')
        await toggle.click()
        await expect
          .poll(() => page.locator('html').evaluate((el) => el.classList.contains('dark')))
          .toBe(requestedTheme === 'Enable dark mode')
        await expect
          .poll(
            () =>
              cells.evaluateAll((elements) =>
                elements.length
                  ? Math.max(
                      ...elements.map((element) => {
                        const { width, height } = element.getBoundingClientRect()
                        return Math.abs(width - height)
                      })
                    )
                  : Number.POSITIVE_INFINITY
              ),
            {
              message: `Contribution cells should be square at ${width}px after theme change ${change}`,
              timeout: 10000,
            }
          )
          .toBeLessThanOrEqual(0.25)
      }
    }
  })

  test('should have user activity sections', async ({ page }) => {
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Recent Issues' })
    ).toBeVisible()
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Recent Pull Requests' })
    ).toBeVisible()
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Repositories' })
    ).toBeVisible()
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Recent Milestones' })
    ).toBeVisible()
    const firstRepo = page.locator('div').filter({ hasText: 'Repositories' }).locator('a').first()
    await expect(firstRepo).toBeVisible()
  })
})
