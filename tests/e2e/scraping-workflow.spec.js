/**
 * E2E Scraping Workflow Tests
 */
const { test, expect } = require('@playwright/test');

test.describe('Complete Scraping Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    
    // Authenticate user
    await page.evaluate(() => {
      sessionStorage.setItem('user', JSON.stringify({ username: 'admin' }));
    });
    
    await page.reload();
  });

  test('complete scraping and WhatsApp workflow', async ({ page }) => {
    let scrapingTriggered = false;
    let whatsappSent = false;

    // Mock scraping trigger
    await page.route('**/api/trigger-scraping', async route => {
      scrapingTriggered = true;
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: '뉴스 스크래핑이 시작되었습니다',
          run_id: 123456789,
          run_url: 'https://github.com/test/repo/actions/runs/123456789'
        })
      });
    });

    // Mock WhatsApp sending
    await page.route('**/api/send-only', async route => {
      whatsappSent = true;
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: 'WhatsApp 메시지가 전송되었습니다'
        })
      });
    });

    // Mock status check to simulate completion
    await page.route('**/api/get-scraping-status', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          runs: [
            {
              id: 123456789,
              status: 'completed',
              conclusion: 'success',
              created_at: '2025-07-24T00:00:00Z',
              updated_at: '2025-07-24T00:05:00Z'
            }
          ]
        })
      });
    });

    // Mock latest scraped data after completion
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
                  title: 'Fresh News Article',
                  url: 'https://example.com/fresh',
                  summary: 'Newly scraped article',
                  site: 'Test Site',
                  group: 'News'
                }
              ],
              article_count: 1
            }
          ],
          lastUpdated: '2025-07-24T00:05:00Z',
          articleCount: 1
        })
      });
    });

    // Step 1: Trigger scraping
    await page.click('#scrapButton');
    
    // Verify scraping was triggered
    await expect(page.locator('.notification.success')).toBeVisible({ timeout: 5000 });
    expect(scrapingTriggered).toBe(true);
    
    // Step 2: Wait for completion (simulate)
    await page.waitForTimeout(2000);
    
    // Step 3: Send WhatsApp message
    await page.click('#sendButton');
    
    // Verify WhatsApp was sent
    await expect(page.locator('.notification.success')).toBeVisible({ timeout: 5000 });
    expect(whatsappSent).toBe(true);
    
    // Step 4: Verify data updated
    await page.reload();
    await expect(page.locator('#todayArticles')).toContainText('1');
  });

  test('scraping only workflow', async ({ page }) => {
    // Mock scrape-only endpoint
    await page.route('**/api/scrape-only', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: '스크래핑만 시작되었습니다',
          run_id: 123456790
        })
      });
    });

    // Look for scrape-only button
    const scrapeOnlyButton = page.locator('button:has-text("스크래핑만")');
    
    if (await scrapeOnlyButton.isVisible()) {
      await scrapeOnlyButton.click();
      
      // Should show success notification
      await expect(page.locator('.notification.success')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('.notification.success')).toContainText('스크래핑만');
    }
  });

  test('WhatsApp only workflow', async ({ page }) => {
    // Mock WhatsApp-only endpoint
    await page.route('**/api/send-only', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: 'WhatsApp 전송이 시작되었습니다',
          run_id: 123456791
        })
      });
    });

    // Click send button
    await page.click('#sendButton');
    
    // Should show success notification
    await expect(page.locator('.notification.success')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.notification.success')).toContainText('WhatsApp');
  });

  test('workflow error handling', async ({ page }) => {
    // Mock scraping failure
    await page.route('**/api/trigger-scraping', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          error: 'GitHub Actions not available'
        })
      });
    });

    // Trigger scraping
    await page.click('#scrapButton');
    
    // Should show error notification
    await expect(page.locator('.notification.error')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.notification.error')).toContainText('Actions');
    
    // Should not proceed to next step
    await expect(page.locator('#loadingSpinner')).not.toBeVisible();
  });

  test('workflow status monitoring', async ({ page }) => {
    let statusChecked = false;

    // Mock status endpoint
    await page.route('**/api/get-scraping-status', async route => {
      statusChecked = true;
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          runs: [
            {
              id: 123456789,
              status: 'in_progress',
              conclusion: null,
              created_at: '2025-07-24T00:00:00Z',
              updated_at: '2025-07-24T00:02:00Z'
            }
          ]
        })
      });
    });

    // Look for status indicator
    const statusIndicator = page.locator('#statusIndicator');
    
    if (await statusIndicator.isVisible()) {
      // Should show current status
      await expect(statusIndicator).toBeVisible();
      
      // If status is checked automatically, verify it happened
      await page.waitForTimeout(3000);
      // Note: This would depend on the actual implementation
    }
  });

  test('workflow with multiple articles', async ({ page }) => {
    // Mock multiple articles response
    await page.route('**/api/get-latest-scraped', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          articles: [
            {
              group: 'News',
              articles: [
                { title: 'News 1', url: 'https://example.com/1', summary: 'Summary 1', site: 'Site 1' },
                { title: 'News 2', url: 'https://example.com/2', summary: 'Summary 2', site: 'Site 2' }
              ],
              article_count: 2
            },
            {
              group: 'Economy',
              articles: [
                { title: 'Economy 1', url: 'https://example.com/3', summary: 'Summary 3', site: 'Site 3' }
              ],
              article_count: 1
            }
          ],
          articleCount: 3
        })
      });
    });

    await page.reload();
    
    // Should show total count
    await expect(page.locator('#todayArticles')).toContainText('3');
    
    // Click to open modal
    await page.click('#todayArticles');
    
    // Should show all articles
    const modal = page.locator('#todayArticlesModal');
    await expect(modal).toBeVisible();
    await expect(modal).toContainText('News 1');
    await expect(modal).toContainText('News 2');
    await expect(modal).toContainText('Economy 1');
  });

  test('workflow data persistence', async ({ page }) => {
    // Mock consistent data
    const mockData = {
      success: true,
      articles: [
        {
          group: 'News',
          articles: [
            {
              title: 'Persistent Article',
              url: 'https://example.com/persistent',
              summary: 'This should persist',
              site: 'Test Site'
            }
          ],
          article_count: 1
        }
      ],
      articleCount: 1
    };

    await page.route('**/api/get-latest-scraped', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify(mockData)
      });
    });

    // Load data
    await page.reload();
    await expect(page.locator('#todayArticles')).toContainText('1');
    
    // Refresh page
    await page.reload();
    
    // Data should persist
    await expect(page.locator('#todayArticles')).toContainText('1');
  });
});