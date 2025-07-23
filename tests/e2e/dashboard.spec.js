/**
 * E2E Dashboard Tests
 */
const { test, expect } = require('@playwright/test');

test.describe('Dashboard Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    
    // Set authenticated state
    await page.evaluate(() => {
      sessionStorage.setItem('user', JSON.stringify({ username: 'admin' }));
    });
    
    await page.reload();
  });

  test('should display dashboard components', async ({ page }) => {
    // Main dashboard elements should be visible
    await expect(page.locator('#dashboard')).toBeVisible();
    await expect(page.locator('#todayArticles')).toBeVisible();
    await expect(page.locator('#latestScrapedArticles')).toBeVisible();
    await expect(page.locator('#scrapButton')).toBeVisible();
    await expect(page.locator('#sendButton')).toBeVisible();
  });

  test('should load latest scraped articles', async ({ page }) => {
    // Mock API response
    await page.route('**/api/get-latest-scraped', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          articles: [
            {
              group: 'News',
              articles: [
                {
                  title: 'Test Article',
                  url: 'https://example.com/test',
                  summary: 'Test summary',
                  site: 'Test Site',
                  group: 'News'
                }
              ],
              article_count: 1
            }
          ],
          lastUpdated: '2025-07-24T00:00:00Z',
          articleCount: 1
        })
      });
    });

    await page.reload();
    
    // Should display article count
    await expect(page.locator('#todayArticles')).toContainText('1');
    
    // Should display articles in the list
    await expect(page.locator('#latestScrapedArticles')).not.toContainText('스크랩된 기사가 없습니다');
  });

  test('should trigger scraping workflow', async ({ page }) => {
    // Mock scraping API
    await page.route('**/api/trigger-scraping', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: '뉴스 스크래핑이 시작되었습니다',
          run_id: 123456789
        })
      });
    });

    // Click scraping button
    await page.click('#scrapButton');
    
    // Should show loading state
    await expect(page.locator('#loadingSpinner')).toBeVisible({ timeout: 1000 });
    
    // Should show success notification
    await expect(page.locator('.notification.success')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.notification.success')).toContainText('스크래핑이 시작');
  });

  test('should handle scraping errors', async ({ page }) => {
    // Mock API error
    await page.route('**/api/trigger-scraping', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          error: 'GitHub token not configured'
        })
      });
    });

    // Click scraping button
    await page.click('#scrapButton');
    
    // Should show error notification
    await expect(page.locator('.notification.error')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.notification.error')).toContainText('token');
  });

  test('should open article modal when clicking article count', async ({ page }) => {
    // Mock articles data
    await page.route('**/api/get-latest-scraped', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          articles: [
            {
              group: 'News',
              articles: [
                {
                  title: 'Test Article 1',
                  url: 'https://example.com/test1',
                  summary: 'Test summary 1',
                  site: 'Test Site'
                },
                {
                  title: 'Test Article 2',
                  url: 'https://example.com/test2',
                  summary: 'Test summary 2',
                  site: 'Test Site'
                }
              ],
              article_count: 2
            }
          ],
          articleCount: 2
        })
      });
    });

    await page.reload();
    
    // Click on article count
    await page.click('#todayArticles');
    
    // Should open modal
    await expect(page.locator('#todayArticlesModal')).toBeVisible();
    await expect(page.locator('#todayArticlesModal')).toContainText('Test Article 1');
    await expect(page.locator('#todayArticlesModal')).toContainText('Test Article 2');
  });

  test('should send WhatsApp message', async ({ page }) => {
    // Mock WhatsApp API
    await page.route('**/api/send-only', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: 'WhatsApp 메시지가 전송되었습니다'
        })
      });
    });

    // Click send button
    await page.click('#sendButton');
    
    // Should show success notification
    await expect(page.locator('.notification.success')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.notification.success')).toContainText('WhatsApp');
  });

  test('should refresh dashboard data', async ({ page }) => {
    let requestCount = 0;
    
    // Count API requests
    await page.route('**/api/get-latest-scraped', async route => {
      requestCount++;
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          articles: [],
          articleCount: 0
        })
      });
    });

    // Initial load
    await page.reload();
    await page.waitForTimeout(1000);
    
    const initialCount = requestCount;
    
    // Click refresh (if refresh button exists)
    const refreshButton = page.locator('#refreshButton');
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      await page.waitForTimeout(1000);
      
      // Should have made another API call
      expect(requestCount).toBeGreaterThan(initialCount);
    }
  });

  test('should navigate between different sections', async ({ page }) => {
    // Test navigation if multiple sections exist
    const sections = ['#homeSection', '#scrapSection', '#historySection', '#settingsSection'];
    
    for (const section of sections) {
      const element = page.locator(section);
      if (await element.isVisible()) {
        await element.click();
        await expect(element).toHaveClass(/active|selected/);
      }
    }
  });

  test('should handle offline state', async ({ page }) => {
    // Go offline
    await page.context().setOffline(true);
    
    // Try to trigger scraping
    await page.click('#scrapButton');
    
    // Should show error or offline message
    await expect(page.locator('.notification.error')).toBeVisible({ timeout: 5000 });
    
    // Go back online
    await page.context().setOffline(false);
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Dashboard should still be functional
    await expect(page.locator('#dashboard')).toBeVisible();
    await expect(page.locator('#scrapButton')).toBeVisible();
    
    // Elements should be properly sized for mobile
    const buttonRect = await page.locator('#scrapButton').boundingBox();
    expect(buttonRect.width).toBeGreaterThan(100); // Should be touch-friendly
    expect(buttonRect.height).toBeGreaterThan(40);
  });
});