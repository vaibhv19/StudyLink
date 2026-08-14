import { test, expect } from '@playwright/test';

test.describe('Authentication & Account Linking E2E Flow', () => {
  test('allows student to register, login, view dashboard, and logout', async ({ page }) => {
    // Intercept Registration API
    await page.route('**/api/v1/auth/register/', async (route) => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          access: 'mock-jwt-access-token-12345',
          user: {
            id: 'usr-e2e-1',
            email: 'student_e2e@example.edu',
            full_name: 'Jordan E2E Student',
            role: 'student',
          },
        }),
      });
    });

    // Intercept Login API
    await page.route('**/api/v1/auth/login/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access: 'mock-jwt-access-token-12345',
          user: {
            id: 'usr-e2e-1',
            email: 'student_e2e@example.edu',
            full_name: 'Jordan E2E Student',
            role: 'student',
          },
        }),
      });
    });

    // Intercept Dashboard API
    await page.route('**/api/v1/dashboard/owner/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          my_listings: [],
          my_active_requests: [],
        }),
      });
    });

    // 1. Visit Auth page
    await page.goto('/auth');
    await expect(page.locator('h2:has-text("Welcome Back")')).toBeVisible();

    // 2. Switch to Register tab
    await page.click('button:has-text("Register")');
    await expect(page.locator('h2:has-text("Create Account")')).toBeVisible();

    // 3. Fill registration form
    await page.fill('input[name="fullName"]', 'Jordan E2E Student');
    await page.fill('input[name="email"]', 'student_e2e@example.edu');
    await page.fill('input[name="password"]', 'StrongPass123!');

    // Submit registration
    await page.click('button:has-text("Create Account")');

    // Verify redirected to Dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('text=Hello, Jordan E2E Student!')).toBeVisible();

    // 4. Logout
    await page.click('button:has-text("Logout")');
    await expect(page.locator('a:has-text("Sign In")')).toBeVisible();
  });

  test('handles OAuth account collision and linking confirmation modal', async ({ page }) => {
    // Intercept social OAuth exchange endpoint returning 409 Account Collision
    await page.route('**/api/v1/auth/social/google/', async (route) => {
      await route.fulfill({
        status: 409,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'account_collision',
          message: 'An account with this email already exists.',
          email: 'collision_student@example.edu',
          provider: 'google',
        }),
      });
    });

    // Intercept link confirmation endpoint
    await page.route('**/api/v1/auth/social/link-confirm/', async (route) => {
      const postData = JSON.parse(route.request().postData() || '{}');
      if (postData.password === 'CorrectLocalPass123!') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            access: 'mock-linked-jwt-token-777',
            user: {
              id: 'usr-collision-1',
              email: 'collision_student@example.edu',
              full_name: 'Linked Google Student',
              role: 'student',
            },
          }),
        });
      } else {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 'invalid_credentials',
            message: 'Invalid password. Account linking rejected.',
          }),
        });
      }
    });

    // Intercept dashboard data
    await page.route('**/api/v1/dashboard/owner/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          my_listings: [],
          my_active_requests: [],
        }),
      });
    });

    // Navigate to OAuth callback URL with code and provider
    await page.goto('/oauth-callback?code=mock-google-code-123&provider=google');

    // Verify Account Link Modal is displayed
    await expect(page.locator('text=Link Google Account')).toBeVisible();
    await expect(page.locator('text=Security Verification Required')).toBeVisible();

    // 1. Submit incorrect password
    await page.fill('input[type="password"]', 'WrongPassword!');
    await page.click('button:has-text("Confirm & Link")');
    await expect(page.locator('text=Invalid password. Account linking rejected.')).toBeVisible();

    // 2. Submit correct password
    await page.fill('input[type="password"]', 'CorrectLocalPass123!');
    await page.click('button:has-text("Confirm & Link")');

    // Verify successful authentication and redirection to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('text=Hello, Linked Google Student!')).toBeVisible();
  });
});
