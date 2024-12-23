const puppeteer = require('puppeteer');

(async () => {
  // Start Puppeteer browser with proxy settings
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--proxy-server=http://localhost:8888'  // Proxy to use mitmproxy
    ]
  });

  const page = await browser.newPage();
  
  // Navigate to the amazon page showing foundation makeup
  await page.goto('https://www.amazon.com/s?k=foundation+makeup')
  // Perform scraping logic
  // solve any captchas
  const data = await page.evaluate(() => {
    // return page title for now for testing
    return document.title;
  });
  
  console.log(data); // Log the scraped data
  
  await browser.close();
})();
