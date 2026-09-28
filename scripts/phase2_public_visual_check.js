const { chromium } = require('./node_modules/playwright');
const fs = require('fs');
const path = require('path');

const baseUrl = 'http://127.0.0.1:3018';
const widths = [320, 375, 390, 430, 768, 1024, 1440, 1600];
const publicRoutes = ['/', '/about', '/login', '/register', '/admin/login', '/emergency', '/emergency/track/EMG-20260926-0001'];
const outputDir = path.resolve(__dirname, '..', 'docs', 'ui-ux-phase-2', 'screenshots', 'after');

async function main() {
  fs.mkdirSync(outputDir, { recursive: true });
  const browser = await chromium.launch({ headless: true, executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const results = [];
  for (const route of publicRoutes) {
    for (const width of widths) {
      await page.setViewportSize({ width, height: 900 });
      const response = await page.goto(`${baseUrl}${route}`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(350);
      const dimensions = await page.evaluate(() => ({
        viewport: document.documentElement.clientWidth,
        document: document.documentElement.scrollWidth,
        body: document.body.scrollWidth,
      }));
      results.push({ route, width, status: response?.status() ?? null, ...dimensions, overflow: dimensions.document > width || dimensions.body > width });
      if (width === 1440) {
        const name = route === '/' ? 'home' : route.split('/').filter(Boolean).join('_').replaceAll('[', '').replaceAll(']', '') || 'home';
        await page.screenshot({ path: path.join(outputDir, `${name}-1440.png`), fullPage: true });
      }
      if (route === '/emergency' && width === 390) {
        await page.screenshot({ path: path.join(outputDir, 'emergency-390.png'), fullPage: true });
      }
    }
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${baseUrl}/`, { waitUntil: 'domcontentloaded' });
  await page.getByRole('button', { name: 'Open navigation menu' }).click({ force: true });
  const menuOpen = await page.getByRole('navigation', { name: 'Mobile navigation' }).isVisible();
  await page.keyboard.press('Escape');
  const menuClosedOnEscape = await page.getByRole('navigation', { name: 'Mobile navigation' }).count() === 0;
  await page.screenshot({ path: path.join(outputDir, 'home-mobile-menu.png'), fullPage: true });
  fs.writeFileSync(path.join(outputDir, 'responsive-results.json'), JSON.stringify({ widths, routes: publicRoutes, results, mobileMenu: { menuOpen, menuClosedOnEscape } }, null, 2));
  await browser.close();
  const failures = results.filter((result) => result.status !== 200 || result.overflow);
  console.log(JSON.stringify({ checked: results.length, widths, failures, mobileMenu: { menuOpen, menuClosedOnEscape }, screenshots: outputDir }, null, 2));
  if (failures.length || !menuOpen || !menuClosedOnEscape) process.exitCode = 1;
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
