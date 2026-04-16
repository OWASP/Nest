import fs from 'node:fs'
import { test, expect } from '@playwright/test'
import slugify from 'utils/slugify'

test.describe('Calendar Export Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { timeout: 25000 })
  })

  test('should download a valid ICS file when clicked', async ({ page }) => {
    const firstEventButton = page.getByRole('button', { name: /Add .* to Calendar/i }).first()
    await expect(firstEventButton).toBeVisible()
    const buttonText =
      (await firstEventButton.getAttribute('aria-label')) || (await firstEventButton.innerText())
    const eventName = buttonText
      .replace(/^Add\s+/i, '')
      .replace(/\s+to Calendar$/i, '') // NOSONAR
      .trim()
    const downloadPromise = page.waitForEvent('download')
    await firstEventButton.click()
    const download = await downloadPromise
    const expectedFilename = `${slugify(eventName)}.ics`
    expect(download.suggestedFilename()).toBe(expectedFilename)
    const path = await download.path()
    expect(path, 'Expected Playwright to provide a download path').toBeTruthy()

    if (path) {
      const content = fs.readFileSync(path, 'utf-8')
      expect(content).toContain('BEGIN:VCALENDAR')
      expect(content).toContain('VERSION:2.0')
      expect(content).toContain('BEGIN:VEVENT')
      expect(content).toContain(`SUMMARY:${eventName}`)
      expect(content).toContain('END:VCALENDAR')
    }
  })
})
