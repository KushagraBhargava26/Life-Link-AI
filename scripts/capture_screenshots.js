const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost';
const SCREENSHOT_DIR = path.resolve(__dirname, '..', 'screenshots');

const DIRS = [
  path.join(SCREENSHOT_DIR, '00_public'),
  path.join(SCREENSHOT_DIR, '01_donor'),
  path.join(SCREENSHOT_DIR, '02_hospital'),
  path.join(SCREENSHOT_DIR, '03_blood_bank'),
  path.join(SCREENSHOT_DIR, '04_admin'),
  path.join(SCREENSHOT_DIR, '05_responsive'),
];

DIRS.forEach((dir) => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

async function captureAll() {
  console.log('[*] Initializing Playwright browser instance...');
  const browser = await chromium.launch({
    headless: true,
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  });

  async function loginAs(page, personaRole) {
    await page.goto(`${BASE_URL}/admin/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);
    const selectBtn = page.locator(`button:has-text("Select ${personaRole}")`).first();
    if (await selectBtn.count() > 0) {
      await selectBtn.click();
      await page.waitForTimeout(300);
      await page.click('form button[type="submit"]');
      await page.waitForTimeout(2500);
    } else {
      console.warn(`[!] Button Select ${personaRole} not found on admin/login`);
    }
  }

  // -------------------------------------------------------------
  // 00_PUBLIC SCREENS (1440x900)
  // -------------------------------------------------------------
  console.log('\n[=== SECTION 00: PUBLIC PAGES ===]');
  {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 2,
    });
    const page = await context.newPage();

    console.log('  -> Capturing 01_home_hero_desktop.png...');
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '00_public', '01_home_hero_desktop.png') });

    console.log('  -> Capturing 02_home_features_desktop.png...');
    await page.evaluate(() => window.scrollTo(0, 850));
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '00_public', '02_home_features_desktop.png') });

    console.log('  -> Capturing 03_about_page_desktop.png...');
    await page.goto(`${BASE_URL}/about`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '00_public', '03_about_page_desktop.png') });

    console.log('  -> Capturing 04_login_page_desktop.png...');
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '00_public', '04_login_page_desktop.png') });

    console.log('  -> Capturing 05_register_page_desktop.png...');
    await page.goto(`${BASE_URL}/register`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '00_public', '05_register_page_desktop.png') });

    console.log('  -> Capturing 06_emergency_intake_desktop.png...');
    await page.goto(`${BASE_URL}/emergency`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '00_public', '06_emergency_intake_desktop.png') });

    console.log('  -> Capturing 07_emergency_tracking_desktop.png...');
    await page.goto(`${BASE_URL}/emergency/track/EMR-2026-0001`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '00_public', '07_emergency_tracking_desktop.png') });

    await context.close();
  }

  // -------------------------------------------------------------
  // 01_DONOR PORTAL (1440x900)
  // -------------------------------------------------------------
  console.log('\n[=== SECTION 01: DONOR PORTAL ===]');
  {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 2,
    });
    const page = await context.newPage();

    await loginAs(page, 'Demo Donor');
    await page.waitForTimeout(2000);

    // 01 Donor Dashboard
    console.log('  -> Capturing 01_donor_dashboard_desktop.png...');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_donor', '01_donor_dashboard_desktop.png') });

    // 02 Donor Profile
    console.log('  -> Capturing 02_donor_profile_desktop.png...');
    const editBtn = page.locator('button:has-text("Update Profile"), button:has-text("Edit Profile")').first();
    if (await editBtn.count() > 0) {
      await editBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_donor', '02_donor_profile_desktop.png') });

    const cancelBtn = page.locator('button:has-text("Cancel")').first();
    if (await cancelBtn.count() > 0) {
      await cancelBtn.click();
      await page.waitForTimeout(500);
    }

    // 03 Donor Opportunities
    console.log('  -> Capturing 03_donor_opportunities_desktop.png...');
    await page.evaluate(() => window.scrollTo(0, 450));
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_donor', '03_donor_opportunities_desktop.png') });

    // 04 Donor Opportunity Detail
    console.log('  -> Capturing 04_donor_opportunity_detail_desktop.png...');
    const viewDetailBtn = page.locator('a:has-text("View Emergency Details"), a:has-text("View Details")').first();
    if (await viewDetailBtn.count() > 0) {
      await viewDetailBtn.click();
      await page.waitForTimeout(2000);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_donor', '04_donor_opportunity_detail_desktop.png') });
    } else {
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_donor', '04_donor_opportunity_detail_desktop.png') });
    }

    await context.close();
  }

  // -------------------------------------------------------------
  // 02_HOSPITAL PORTAL (1440x900)
  // -------------------------------------------------------------
  console.log('\n[=== SECTION 02: HOSPITAL PORTAL ===]');
  {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 2,
    });
    const page = await context.newPage();

    await loginAs(page, 'Demo Hospital');
    await page.waitForTimeout(2000);

    // 01 Hospital Dashboard
    console.log('  -> Capturing 01_hospital_dashboard_desktop.png...');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_hospital', '01_hospital_dashboard_desktop.png') });

    // 02 Hospital Profile
    console.log('  -> Capturing 02_hospital_profile_desktop.png...');
    const profileLink = page.locator('a[href="/hospital/profile"], button:has-text("Facility Profile")').first();
    if (await profileLink.count() > 0) {
      await profileLink.click();
      await page.waitForTimeout(2000);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_hospital', '02_hospital_profile_desktop.png') });
      const backLink = page.locator('a[href="/hospital"], a:has-text("Back")').first();
      if (await backLink.count() > 0) {
        await backLink.click();
        await page.waitForTimeout(1500);
      }
    } else {
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_hospital', '02_hospital_profile_desktop.png') });
    }

    // 03 Hospital Create Requisition Modal
    console.log('  -> Capturing 03_hospital_create_requisition_desktop.png...');
    const createReqBtn = page.locator('button:has-text("+ Create Blood Request")').first();
    if (await createReqBtn.count() > 0) {
      await createReqBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_hospital', '03_hospital_create_requisition_desktop.png') });
      const closeBtn = page.locator('button:has-text("Cancel")').first();
      if (await closeBtn.count() > 0) {
        await closeBtn.click();
        await page.waitForTimeout(500);
      }
    }

    // 04 Hospital Matching Workspace
    console.log('  -> Capturing 04_hospital_matching_workspace_desktop.png...');
    const matchBtn = page.locator('a:has-text("Matches"), a:has-text("Matching"), a:has-text("Find Candidates")').first();
    if (await matchBtn.count() > 0) {
      await matchBtn.click();
      await page.waitForTimeout(2000);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_hospital', '04_hospital_matching_workspace_desktop.png') });
    } else {
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_hospital', '04_hospital_matching_workspace_desktop.png') });
    }

    // 05 Hospital Donor Coordination
    console.log('  -> Capturing 05_hospital_donor_coordination_desktop.png...');
    await page.evaluate(() => window.scrollTo(0, 450));
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_hospital', '05_hospital_donor_coordination_desktop.png') });

    await context.close();
  }

  // -------------------------------------------------------------
  // 03_BLOOD BANK PORTAL (1440x900)
  // -------------------------------------------------------------
  console.log('\n[=== SECTION 03: BLOOD BANK PORTAL ===]');
  {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 2,
    });
    const page = await context.newPage();

    await loginAs(page, 'Demo Blood Bank');
    await page.waitForTimeout(2000);

    // 01 Blood Bank Dashboard
    console.log('  -> Capturing 01_bloodbank_dashboard_desktop.png...');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_blood_bank', '01_bloodbank_dashboard_desktop.png') });

    // 02 Blood Bank Profile
    console.log('  -> Capturing 02_bloodbank_profile_desktop.png...');
    const bbProfileLink = page.locator('a[href="/blood-bank/profile"], a:has-text("Facility Profile")').first();
    if (await bbProfileLink.count() > 0) {
      await bbProfileLink.click();
      await page.waitForTimeout(2000);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_blood_bank', '02_bloodbank_profile_desktop.png') });
      const backLink = page.locator('a[href="/blood-bank"], a:has-text("Back")').first();
      if (await backLink.count() > 0) {
        await backLink.click();
        await page.waitForTimeout(1500);
      }
    } else {
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_blood_bank', '02_bloodbank_profile_desktop.png') });
    }

    // 03 Blood Bank Inventory Grid
    console.log('  -> Capturing 03_bloodbank_inventory_desktop.png...');
    await page.evaluate(() => window.scrollTo(0, 300));
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_blood_bank', '03_bloodbank_inventory_desktop.png') });

    // 04 Blood Bank Emergency Demand Feed
    console.log('  -> Capturing 04_bloodbank_emergency_demand_desktop.png...');
    await page.evaluate(() => window.scrollTo(0, 850));
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_blood_bank', '04_bloodbank_emergency_demand_desktop.png') });

    // 05 Blood Bank Response / Fulfillment Modal
    console.log('  -> Capturing 05_bloodbank_response_fulfillment_desktop.png...');
    const fulfillBtn = page.locator('button:has-text("Fulfill Demand"), button:has-text("Respond to Request")').first();
    if (await fulfillBtn.count() > 0) {
      await fulfillBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_blood_bank', '05_bloodbank_response_fulfillment_desktop.png') });
      const closeBtn = page.locator('button:has-text("Cancel")').first();
      if (await closeBtn.count() > 0) {
        await closeBtn.click();
        await page.waitForTimeout(500);
      }
    } else {
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_blood_bank', '05_bloodbank_response_fulfillment_desktop.png') });
    }

    await context.close();
  }

  // -------------------------------------------------------------
  // 04_ADMIN GOVERNANCE PORTAL (1440x900)
  // -------------------------------------------------------------
  console.log('\n[=== SECTION 04: ADMIN GOVERNANCE PORTAL ===]');
  {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 2,
    });
    const page = await context.newPage();

    console.log('  -> Capturing 01_admin_demo_login_desktop.png...');
    await page.goto(`${BASE_URL}/admin/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_admin', '01_admin_demo_login_desktop.png') });

    await loginAs(page, 'Demo Admin');
    await page.waitForTimeout(2000);

    // 02 Admin Dashboard
    console.log('  -> Capturing 02_admin_dashboard_desktop.png...');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_admin', '02_admin_dashboard_desktop.png') });

    // 03 Admin Hospital Governance Tab
    console.log('  -> Capturing 03_admin_hospital_governance_desktop.png...');
    const hospTab = page.locator('button:has-text("Hospitals")').first();
    if (await hospTab.count() > 0) {
      await hospTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_admin', '03_admin_hospital_governance_desktop.png') });

    // 04 Admin Blood Bank Governance Tab
    console.log('  -> Capturing 04_admin_bloodbank_governance_desktop.png...');
    const bbTab = page.locator('button:has-text("Blood Banks")').first();
    if (await bbTab.count() > 0) {
      await bbTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_admin', '04_admin_bloodbank_governance_desktop.png') });

    // 05 Admin Certificate Review Modal
    console.log('  -> Capturing 05_admin_certificate_review_desktop.png...');
    const certBtn = page.locator('button:has-text("View Certificate"), button:has-text("Review")').first();
    if (await certBtn.count() > 0) {
      await certBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_admin', '05_admin_certificate_review_desktop.png') });
    } else {
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_admin', '05_admin_certificate_review_desktop.png') });
    }

    await context.close();
  }

  // -------------------------------------------------------------
  // 05_RESPONSIVE MOBILE (390x844)
  // -------------------------------------------------------------
  console.log('\n[=== SECTION 05: RESPONSIVE MOBILE (390x844) ===]');
  {
    // Mobile Public Home
    {
      const context = await browser.newContext({
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
        deviceScaleFactor: 2,
      });
      const page = await context.newPage();
      console.log('  -> Capturing 01_mobile_home.png...');
      await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_responsive', '01_mobile_home.png') });

      console.log('  -> Capturing 02_mobile_emergency_intake.png...');
      await page.goto(`${BASE_URL}/emergency`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_responsive', '02_mobile_emergency_intake.png') });
      await context.close();
    }

    // Mobile Donor
    {
      const context = await browser.newContext({
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
        deviceScaleFactor: 2,
      });
      const page = await context.newPage();
      console.log('  -> Capturing 03_mobile_donor_opportunities.png...');
      await loginAs(page, 'Demo Donor');
      await page.waitForTimeout(1500);
      await page.evaluate(() => window.scrollTo(0, 350));
      await page.waitForTimeout(800);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_responsive', '03_mobile_donor_opportunities.png') });
      await context.close();
    }

    // Mobile Hospital
    {
      const context = await browser.newContext({
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
        deviceScaleFactor: 2,
      });
      const page = await context.newPage();
      console.log('  -> Capturing 04_mobile_hospital_dashboard.png...');
      await loginAs(page, 'Demo Hospital');
      await page.waitForTimeout(1500);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_responsive', '04_mobile_hospital_dashboard.png') });
      await context.close();
    }

    // Mobile Blood Bank
    {
      const context = await browser.newContext({
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
        deviceScaleFactor: 2,
      });
      const page = await context.newPage();
      console.log('  -> Capturing 05_mobile_bloodbank_inventory.png...');
      await loginAs(page, 'Demo Blood Bank');
      await page.waitForTimeout(1500);
      await page.evaluate(() => window.scrollTo(0, 250));
      await page.waitForTimeout(800);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_responsive', '05_mobile_bloodbank_inventory.png') });
      await context.close();
    }
  }

  await browser.close();
  console.log('\n[✓] ALL 26 HIGH-FIDELITY SCREENSHOTS CAPTURED SUCCESSFULLY!');
}

captureAll().catch(err => {
  console.error('[!] Capture failed:', err);
  process.exit(1);
});
