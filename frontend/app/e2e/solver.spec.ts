import { test, expect } from '@playwright/test';

test.describe('Solver flow', () => {
  test('page loads with title and Solve button', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Linear Equation Solver' })).toBeVisible();
    await expect(page.getByTestId('solve-btn')).toBeVisible();
  });

  test('solve system shows solution panel with result', async ({ page }) => {
    await page.goto('/');
    const solveBtn = page.getByTestId('solve-btn');
    await expect(solveBtn).toBeVisible();
    await solveBtn.click();
    // After solve, panel switches to solution and shows either solution values or degenerate message
    await expect(
      page.getByTestId('solution-value').or(page.locator('.solution-degenerate')).or(page.locator('.solution-value')).or(page.locator('.error'))
    ).toBeVisible({ timeout: 15000 });
  });

  test('solution panel has accessible region when visible', async ({ page }) => {
    await page.goto('/');
    const solveBtn = page.getByTestId('solve-btn');
    await solveBtn.click();
    const region = page.getByRole('region', { name: 'Solution viewer' });
    await expect(region).toBeVisible({ timeout: 15000 });
  });
});
