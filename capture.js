/**
 * Phase 1: Visual Capture
 * Uses Playwright in headless mode to capture the app UI
 * Environment Variables:
 *   APP_URL - The app URL to capture (required)
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// Use environment variable APP_URL or fallback for local testing
const REPLIT_URL = process.env.APP_URL || process.argv[2] || 'https://f21467cc-364a-4249-bae9-b4e193ff390f-00-yzv5rigbah39.pike.replit.dev/';
const RECORDINGS_DIR = path.join(__dirname, 'recordings');
const OUTPUT_FILE = path.join(RECORDINGS_DIR, 'raw_video.webm');

// Ensure recordings directory exists
if (!fs.existsSync(RECORDINGS_DIR)) {
  fs.mkdirSync(RECORDINGS_DIR, { recursive: true });
}

async function performHumanLikeActions(page) {
  // Wait for the main app container to load
  console.log('Waiting for app to load...');
  try {
    await page.waitForSelector('#root', { timeout: 30000 });
    console.log('App container #root found');
  } catch (e) {
    console.log('Warning: #root not found, continuing...');
  }
  
  // Wait for network to settle
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  
  // Scroll through the features
  console.log('Scrolling through features...');
  for (let i = 0; i < 3; i++) {
    await page.evaluate(() => {
      window.scrollBy({ top: Math.random() * 300 + 100, behavior: 'smooth' });
    });
    await page.waitForTimeout(500 + Math.random() * 500);
  }
  
  // Scroll back up
  await page.evaluate(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  await page.waitForTimeout(500);
  
  // Click on 'Admin Dashboard' link if exists
  console.log('Looking for Admin Dashboard link...');
  const adminLink = await page.$('a[href*="admin"], a:has-text("Admin"), a:has-text("Dashboard")');
  if (adminLink) {
    try {
      await adminLink.click();
      await page.waitForTimeout(3000);
      console.log('Clicked Admin Dashboard');
    } catch (e) {
      console.log('Admin Dashboard not found, clicking first link');
    }
  }
  
  // Wait for API key content to load
  console.log('Waiting for content to render...');
  await page.waitForTimeout(3000);
  
  // Simulate API key management demonstration
  console.log('Simulating API key management...');
  await page.waitForTimeout(5000);
}

async function captureScreen() {
  console.log('Starting visual capture...');
  console.log(`Target URL: ${REPLIT_URL}`);
  
  const browser = await chromium.launch({ headless: true });
  
  const context = await browser.newContext({
    viewport: { width: 1080, height: 1920 },
    recordVideo: {
      dir: RECORDINGS_DIR,
      size: { width: 1080, height: 1920 }
    }
  });
  
  const page = await context.newPage();
  
  try {
    console.log('Navigating to Replit app...');
    await page.goto(REPLIT_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    
    // Perform human-like actions
    console.log('Performing human-like actions...');
    await performHumanLikeActions(page);
    
    console.log(`Recording saved to: ${OUTPUT_FILE}`);
  } catch (error) {
    console.error('Error during capture:', error.message);
    throw error;
  } finally {
    await context.close();
    await browser.close();
  }
  
  // Check if video file was created
  const videoFiles = fs.readdirSync(RECORDINGS_DIR).filter(f => f.endsWith('.webm'));
  if (videoFiles.length > 0) {
    const videoFile = path.join(RECORDINGS_DIR, videoFiles[0]);
    fs.renameSync(videoFile, OUTPUT_FILE);
    console.log(`Video saved as: ${OUTPUT_FILE}`);
  } else {
    console.log('No video file found');
  }
  
  return OUTPUT_FILE;
}

// Run if called directly
if (require.main === module) {
  captureScreen()
    .then(videoPath => {
      console.log('Capture complete:', videoPath);
      process.exit(0);
    })
    .catch(error => {
      console.error('Capture failed:', error);
      process.exit(1);
    });
}

module.exports = { captureScreen, REPLIT_URL };