/**
 * E2E Authentication Tests
 */
const { test, expect } = require('@playwright/test');

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Clear any existing authentication
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.clear();
    });
  });

  test('should show login form when not authenticated', async ({ page }) => {
    await expect(page.locator('#loginForm')).toBeVisible();
    await expect(page.locator('#loginButton')).toBeVisible();
    await expect(page.locator('#username')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    // Mock the API response
    await page.route('**/api/auth', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: '로그인 성공'
        })
      });
    });

    // Fill login form
    await page.fill('#username', 'admin');
    await page.fill('#password', 'Admin@123');
    
    // Submit form
    await page.click('#loginButton');
    
    // Should show success notification
    await expect(page.locator('.notification.success')).toBeVisible({ timeout: 5000 });
    
    // Should hide login form and show dashboard
    await expect(page.locator('#loginForm')).not.toBeVisible();
    await expect(page.locator('#dashboard')).toBeVisible();
  });

  test('should show error on invalid credentials', async ({ page }) => {
    // Mock API error response
    await page.route('**/api/auth', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          error: '잘못된 사용자명 또는 비밀번호입니다'
        })
      });
    });

    // Fill with wrong credentials
    await page.fill('#username', 'wrong');
    await page.fill('#password', 'wrong');
    
    // Submit form
    await page.click('#loginButton');
    
    // Should show error notification
    await expect(page.locator('.notification.error')).toBeVisible({ timeout: 5000 });
    
    // Should still show login form
    await expect(page.locator('#loginForm')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // First login
    await page.evaluate(() => {
      sessionStorage.setItem('user', JSON.stringify({ username: 'admin' }));
    });
    
    await page.reload();
    
    // Should show dashboard
    await expect(page.locator('#dashboard')).toBeVisible();
    await expect(page.locator('#logoutButton')).toBeVisible();
    
    // Click logout
    await page.click('#logoutButton');
    
    // Should show login form again
    await expect(page.locator('#loginForm')).toBeVisible();
    await expect(page.locator('#dashboard')).not.toBeVisible();
  });

  test('should persist login state on page reload', async ({ page }) => {
    // Set authenticated state
    await page.evaluate(() => {
      sessionStorage.setItem('user', JSON.stringify({ username: 'admin' }));
    });
    
    await page.reload();
    
    // Should show dashboard, not login form
    await expect(page.locator('#dashboard')).toBeVisible();
    await expect(page.locator('#loginForm')).not.toBeVisible();
  });
});