import { test, expect } from '@playwright/test';

test.describe('Marketplace State Machine E2E Flow', () => {
  test('executes 2-user giveaway listing, request, acceptance, and handoff completion', async ({ page }) => {
    let listingStatus = 'AVAILABLE';
    let requestStatus = 'NONE';
    const listingId = 'lst-test-market-777';
    const requestId = 'req-test-999';

    // Mock Core Metadata
    await page.route('**/api/v1/core/subjects/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ subjects: [{ id: 1, name: 'Physics' }] }),
      });
    });

    await page.route('**/api/v1/core/courses/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ courses: [{ id: 1, name: 'General Physics', code: 'PHYS101' }] }),
      });
    });

    // Mock Login endpoint
    await page.route('**/api/v1/auth/login/', async (route) => {
      const postData = JSON.parse(route.request().postData() || '{}');
      if (postData.email.includes('owner')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            access: 'mock-owner-token',
            user: { id: 'usr-owner-1', email: 'owner@example.edu', full_name: 'Owner User' },
          }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            access: 'mock-requester-token',
            user: { id: 'usr-requester-2', email: 'buyer@example.edu', full_name: 'Requester Student' },
          }),
        });
      }
    });

    // Mock Marketplace APIs
    await page.route('**/api/v1/market/**', async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      if (url.includes(`/market/${listingId}/request/`)) {
        requestStatus = 'PENDING';
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({ id: requestId, listing_id: listingId, status: 'PENDING' }),
        });
      } else if (url.includes(`/market/${listingId}/complete/`)) {
        listingStatus = 'GIVEN_AWAY';
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: listingId, status: 'GIVEN_AWAY' }),
        });
      } else if (url.includes(`/market/requests/${requestId}/accept/`)) {
        listingStatus = 'REQUESTED';
        requestStatus = 'ACCEPTED';
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: requestId, status: 'ACCEPTED' }),
        });
      } else if (url.includes(`/market/${listingId}/`)) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: listingId,
            title: 'Organic Chemistry Model Kit',
            description: 'Full molecular kit with all pieces intact.',
            pickup_area: 'Student Union 2nd Floor',
            condition: 'Like New',
            status: listingStatus,
            photo_url: 'https://example.com/kit.jpg',
            owner: { id: 'usr-owner-1', full_name: 'Owner User' },
            has_requested: requestStatus === 'PENDING' || requestStatus === 'ACCEPTED',
          }),
        });
      } else if (method === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: listingId,
            title: 'Organic Chemistry Model Kit',
            pickup_area: 'Student Union 2nd Floor',
            condition: 'Like New',
            status: listingStatus,
          }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            count: 1,
            next: null,
            previous: null,
            results: [
              {
                id: listingId,
                title: 'Organic Chemistry Model Kit',
                pickup_area: 'Student Union 2nd Floor',
                condition: 'Like New',
                status: listingStatus,
                photo_url: 'https://example.com/kit.jpg',
                owner_id: 'usr-owner-1',
              },
            ],
          }),
        });
      }
    });

    // Mock Dashboard / Owner Dashboard API
    await page.route('**/api/v1/dashboard/owner/**', async (route) => {
      const recentReqs =
        requestStatus === 'PENDING' || requestStatus === 'ACCEPTED'
          ? [
              {
                id: requestId,
                user_name: 'Requester Student',
                user_email: 'buyer@example.edu',
                status: requestStatus,
                created_at: new Date().toISOString(),
              },
            ]
          : [];
      const pendingReqs =
        requestStatus === 'PENDING'
          ? [
              {
                id: requestId,
                listing_id: listingId,
                listing_title: 'Organic Chemistry Model Kit',
                user_name: 'Requester Student',
                user_email: 'buyer@example.edu',
                created_at: new Date().toISOString(),
              },
            ]
          : [];

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          my_listings: [
            {
              id: listingId,
              title: 'Organic Chemistry Model Kit',
              status: listingStatus,
              request_count: requestStatus === 'PENDING' ? 1 : 0,
              pickup_area: 'Student Union 2nd Floor',
              recent_requests: recentReqs,
            },
          ],
          my_active_requests: pendingReqs,
        }),
      });
    });

    // ==========================================
    // STEP 1: Owner (User A) Logs In & Creates Listing
    // ==========================================
    await page.goto('/auth');
    await page.fill('input[name="email"]', 'owner@example.edu');
    await page.fill('input[name="password"]', 'StrongPass123!');
    await page.click('button[type="submit"]:has-text("Sign In")');
    await expect(page).toHaveURL(/.*dashboard/);

    // Navigate to Marketplace
    await page.click('nav >> text=Marketplace');
    await expect(page.locator('h1:has-text("Giveaway Marketplace")')).toBeVisible();

    // Click Give Away Item
    await page.click('button:has-text("Give Away Item")');
    await expect(page.locator('h1:has-text("Create Giveaway Listing")')).toBeVisible();

    // Fill form
    await page.fill('input[placeholder*="Calculator"]', 'Organic Chemistry Model Kit');
    await page.fill('input[placeholder*="Science Library"]', 'Student Union 2nd Floor');

    // Attach mock photo
    await page.setInputFiles('input[type="file"]', {
      name: 'model_kit.jpg',
      mimeType: 'image/jpeg',
      buffer: Buffer.from('mock-jpeg-bytes'),
    });

    // Submit Listing
    await page.click('button[type="submit"]:has-text("Publish Giveaway")');
    await expect(page).toHaveURL(new RegExp(`/market/${listingId}`));

    // ==========================================
    // STEP 2: Buyer (User B) Logs In & Requests Item
    // ==========================================
    // Logout Owner
    await page.click('button:has-text("Logout")');

    // Login as Requester
    await page.goto('/auth');
    await page.fill('input[name="email"]', 'buyer@example.edu');
    await page.fill('input[name="password"]', 'StrongPass123!');
    await page.click('button[type="submit"]:has-text("Sign In")');
    await expect(page).toHaveURL(/.*dashboard/);

    // Open Listing Detail via Marketplace
    await page.click('nav >> text=Marketplace');
    await page.click('text=Organic Chemistry Model Kit');
    await expect(page).toHaveURL(new RegExp(`/market/${listingId}`));

    // Request the item
    await expect(page.locator('button:has-text("Request Item for Pickup")')).toBeVisible();
    await page.click('button:has-text("Request Item for Pickup")');

    // Verify button updates to Pending Request state
    await expect(page.locator('text=⏳ Request Pending')).toBeVisible();

    // ==========================================
    // STEP 3: Owner Opens Owner Console, Accepts Request & Completes Handoff
    // ==========================================
    // Logout Buyer
    await page.click('button:has-text("Logout")');

    // Login back as Owner
    await page.goto('/auth');
    await page.fill('input[name="email"]', 'owner@example.edu');
    await page.fill('input[name="password"]', 'StrongPass123!');
    await page.click('button[type="submit"]:has-text("Sign In")');
    await expect(page).toHaveURL(/.*dashboard/);

    // Navigate to Owner Console
    await page.click('nav >> text=Owner Console');
    await expect(page.locator('h1:has-text("Exchange Management Hub")')).toBeVisible();

    // Verify incoming request is listed
    await expect(page.locator('text=Requester Student')).toBeVisible();
    await expect(page.locator('button:has-text("Accept")')).toBeVisible();

    // Owner accepts request
    await page.click('button:has-text("Accept")');

    // Verify listing shows Handoff in Progress & Confirm Item Handoff button
    await expect(page.locator('text=⏳ Handoff in Progress')).toBeVisible();
    await expect(page.locator('button:has-text("Confirm Item Handoff")')).toBeVisible();

    // Owner confirms item handoff
    await page.click('button:has-text("Confirm Item Handoff")');

    // Verify listing is marked as given away
    await expect(
      page.locator('text=✓ Handoff Completed & Item Given Away')
    ).toBeVisible();
  });
});
