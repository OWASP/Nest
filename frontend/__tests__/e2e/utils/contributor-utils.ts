import { Page, expect } from '@playwright/test';

export async function expectContributorVisible(page: Page, name: string, extra: string): Promise<void> {
  await expect(page.getByRole('img', { name })).toBeVisible();
  await expect(page.getByText(name)).toBeVisible();
  await expect(page.getByText(extra)).toBeVisible();
}
