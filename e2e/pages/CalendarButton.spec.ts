import fs from 'node:fs'
import { test, expect } from '@playwright/test'
import formatIcsText from 'utils/formatIcsText'
import slugify from 'utils/slugify'

test.describe('Calendar Export Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Upcoming Events' })
    ).toBeVisible()
    await expect(page.getByRole('button', { name: /Add .* to Calendar/i }).first()).toBeVisible()
  })

  test('should download a valid ICS file when clicked', async ({ page }) => {
    const firstEventButton = page.getByRole('button', { name: /Add .* to Calendar/i }).first()
    const buttonText =
      (await firstEventButton.getAttribute('aria-label')) || (await firstEventButton.innerText())
    const eventName = buttonText
      .replace(/^Add\s+/i, '')
      .replace(/\s+to Calendar$/i, '') // NOSONAR
      .trim()
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 30_000 }),
      firstEventButton.click(),
    ])
    const expectedFilename = `${slugify(eventName)}.ics`
    expect(download.suggestedFilename()).toBe(expectedFilename)
    const path = await download.path()
    expect(path, 'Expected Playwright to provide a download path').toBeTruthy()
    const content = fs.readFileSync(path, 'utf-8')
    expect(content).toContain('BEGIN:VCALENDAR')
    expect(content).toContain('VERSION:2.0')
    expect(content).toContain('BEGIN:VEVENT')
    expect(content).toContain(`SUMMARY:${formatIcsText(eventName)}`)
    expect(content).toContain('END:VCALENDAR')
  })
})
