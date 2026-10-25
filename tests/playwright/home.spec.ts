import { createRequire } from "node:module";
import { resolve } from "node:path";

// The spec lives outside frontend; resolve the runner from its locked package.
const frontendRequire = createRequire(resolve(__dirname, "../../frontend/package.json"));
const { test, expect } = frontendRequire("@playwright/test") as typeof import("@playwright/test");

test("home page loads", async ({ page }) => {
  await page.route("**/gc10/metrics", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({ status: "not_trained" })
  }));
  await page.goto("/");

  // Ensure page fully loads
  await page.waitForLoadState("networkidle");

  // Basic sanity check: page has visible body
  await expect(page.locator("body")).toBeVisible();

  // Ensure no error text is visible
  await expect(page.locator("text=Error")).toHaveCount(0);
  await page.getByRole("button", { name: "GC10 experiment", exact: true }).click();
  await expect(page.getByRole("heading", { name: "GC10 local experiment" })).toBeVisible();
  await expect(page.getByText("No trained GC10 results are available yet.")).toBeVisible();
});
