import { test, expect } from "@playwright/test";

test("home page loads", async ({ page }) => {
  await page.goto("http://localhost:5173/");

  // Ensure page fully loads
  await page.waitForLoadState("networkidle");

  // Basic sanity check: page has visible body
  await expect(page.locator("body")).toBeVisible();

  // Ensure no error text is visible
  await expect(page.locator("text=Error")).toHaveCount(0);
});
