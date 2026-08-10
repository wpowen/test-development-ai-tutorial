import { test, expect } from '@playwright/test';

test('valid login shows dashboard', async ({ page }) => {
  await page.goto('https://example.test/login');
  await page.getByLabel('Email').fill('qa@example.test');
  await page.getByLabel('Password').fill('test-password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByTestId('account-status')).toHaveText('Active');
});
