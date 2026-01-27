import fs from 'node:fs'
import { test, expect, Page } from '@playwright/test'
import slugify from 'utils/slugify'

test.describe.serial('Calendar Export Functionality', () => {
  let page: Page
  test.beforeAll(async ({ browser }) => {
    const context = await browser.newContext()
    page = await context.newPage()
    await page.goto('/', { timeout: 25000 })
  })
  test.afterAll(async () => {
    await page.close()
  })

  test('should download a valid ICS file when clicked', async () => {
    const calendarButton = page.getByRole('button', { name: 'Add Event 1 to Calendar' })
    await expect(calendarButton).toBeVisible()

    const downloadPromise = page.waitForEvent('download')

    await calendarButton.click()

    const download = await downloadPromise

    expect(download.suggestedFilename()).toBe(`${slugify('Event 1')}.ics`)

    const path = await download.path()
    expect(path, 'Expected Playwright to provide a download path').toBeTruthy()
    const content = fs.readFileSync(path, 'utf-8')

    expect(content).toContain('BEGIN:VCALENDAR')
    expect(content).toContain('VERSION:2.0')
    expect(content).toContain('BEGIN:VEVENT')

    expect(content).toContain('SUMMARY:')
    expect(content).toContain('END:VCALENDAR')
  })
})
