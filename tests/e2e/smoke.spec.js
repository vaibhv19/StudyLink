import { test, expect } from '@playwright/test';

test.describe('E2E Framework Scaffolding Smoke Test', () => {
  test('launches browser and renders StudyLink home page', async ({ page }) => {
    await page.goto('/');

    // Verify title and main brand heading
    await expect(page).toHaveTitle(/StudyLink|Vite/i);
    await expect(page.locator('text=Peer-to-Peer Hub')).toBeVisible();

    // Verify navigation links
    await expect(page.locator('nav >> text=Resource Vault')).toBeVisible();
    await expect(page.locator('nav >> text=Marketplace')).toBeVisible();
    await expect(page.locator('text=Sign In')).toBeVisible();
  });
});
