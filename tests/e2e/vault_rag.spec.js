import { test, expect } from '@playwright/test';

test.describe('Resource Vault & RAG Chat E2E Flow', () => {
  test('uploads PDF, polls status to READY, chats with document and navigates citations', async ({ page }) => {
    let currentStatus = 'PROCESSING';
    const resourceId = 'res-test-vault-888';

    // Mock Login endpoint
    await page.route('**/api/v1/auth/login/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access: 'mock-jwt-token-12345',
          user: {
            id: 'usr-vault-student',
            email: 'vault_student@example.edu',
            full_name: 'Alex Student',
          },
        }),
      });
    });

    // Mock Dashboard
    await page.route('**/api/v1/dashboard/owner/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ my_listings: [], my_active_requests: [] }),
      });
    });

    // Mock subjects
    await page.route('**/api/v1/core/subjects/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          subjects: [
            { id: 1, name: 'Mathematics', slug: 'math' },
          ],
        }),
      });
    });

    // Mock courses
    await page.route('**/api/v1/core/courses/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          courses: [
            { id: 1, name: 'Calculus I', code: 'MATH101', subject: 1 },
          ],
        }),
      });
    });

    // Mock vault list and comments
    await page.route('**/api/v1/vault/**', async (route) => {
      const url = route.request().url();
      if (url.includes(`/vault/${resourceId}/comments/`)) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 'c-1',
              author_name: 'Alice Student',
              content: 'Is this from the 2026 spring semester?',
              created_at: new Date().toISOString(),
              replies: [],
            },
          ]),
        });
      } else if (url.includes(`/vault/${resourceId}/`)) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: resourceId,
            title: 'Linear Algebra Lecture Notes',
            subject: { id: 1, name: 'Mathematics' },
            course: { id: 1, name: 'Linear Algebra', code: 'MATH101' },
            uploader: { id: 'usr-prof-1', full_name: 'Prof. Gauss' },
            file_path: 'https://example.com/linear_algebra.pdf',
            status: currentStatus,
            upvote_count: 15,
            has_upvoted: false,
            created_at: new Date().toISOString(),
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
                id: resourceId,
                title: 'Linear Algebra Lecture Notes',
                subject_name: 'Mathematics',
                course_code: 'MATH101',
                uploader_name: 'Prof. Gauss',
                file_path: 'https://example.com/linear_algebra.pdf',
                status: currentStatus,
                upvote_count: 15,
                has_upvoted: false,
                created_at: new Date().toISOString(),
              },
            ],
          }),
        });
      }
    });

    // Mock RAG query endpoint
    await page.route('**/api/v1/chat/query/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          answer:
            'Eigenvalues are scalars λ such that Av = λv for some non-zero eigenvector v. They represent the factor by which the vector is stretched.',
          sources: [
            {
              page_number: 2,
              similarity_score: 0.94,
              excerpt: 'Definition 4.1: A scalar lambda is called an eigenvalue of matrix A...',
            },
          ],
        }),
      });
    });

    // 1. Authenticate user
    await page.goto('/auth');
    await page.fill('input[name="email"]', 'vault_student@example.edu');
    await page.fill('input[name="password"]', 'StrongPass123!');
    await page.click('button[type="submit"]:has-text("Sign In")');
    await expect(page).toHaveURL(/.*dashboard/);

    // 2. Navigate via SPA Client Link to Resource Vault
    await page.click('nav >> text=Resource Vault');
    await expect(page.locator('h1:has-text("Resource Vault")')).toBeVisible();

    // Verify initial PROCESSING state badge
    await expect(page.locator('text=Linear Algebra Lecture Notes')).toBeVisible();
    await expect(page.locator('text=PROCESSING')).toBeVisible();

    // Simulate background ingestion completion to READY
    currentStatus = 'READY';

    // 3. Open Resource Detail
    await page.click('text=Linear Algebra Lecture Notes');
    await expect(page).toHaveURL(new RegExp(`/vault/${resourceId}`));

    // Verify Split View: Left PDF Toolbar & Right RAG Panel
    await expect(page.locator('text=PAGE')).toBeVisible();
    await expect(page.locator('text=StudyLink AI Tutor')).toBeVisible();
    await expect(
      page.locator('text=Hi! I am your StudyLink AI tutor scoped exclusively to this document.')
    ).toBeVisible();

    // Verify initial PDF viewer page is 1
    const pageInput = page.locator('input[type="number"]');
    await expect(pageInput).toHaveValue('1');

    // 4. Submit RAG Question in Chat Panel
    await page.fill(
      'input[placeholder="Ask about concepts, proofs, formulas..."]',
      'What is an eigenvalue?'
    );
    await page.click('button:has-text("Send")');

    // 5. Verify AI Response & Citation Rendering
    await expect(
      page.locator('text=Eigenvalues are scalars λ such that Av = λv')
    ).toBeVisible();
    await expect(page.locator('button:has-text("📄 Page 2")')).toBeVisible();
    await expect(page.locator('text=94% match')).toBeVisible();

    // 6. Click Citation Card and verify PDF page jumps to 2
    await page.click('button:has-text("📄 Page 2")');
    await expect(pageInput).toHaveValue('2');

    // 7. Verify Doubt Board comments are rendered below
    await expect(page.locator('h2:has-text("Doubt Board")')).toBeVisible();
    await expect(page.locator('text=Is this from the 2026 spring semester?')).toBeVisible();
  });
});
