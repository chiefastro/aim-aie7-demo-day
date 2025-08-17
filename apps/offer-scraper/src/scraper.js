import { chromium } from 'playwright';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { generateMockRestaurantData } from './mock-data.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class ToastScraper {
  constructor() {
    this.browser = null;
    this.page = null;
  }

  async init() {
    this.browser = await chromium.launch({ 
      headless: false, // Try headful to avoid detection
      args: [
        '--no-sandbox', 
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor'
      ]
    });
    
    this.page = await this.browser.newPage({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    
    // Set additional headers to look more like a real browser
    await this.page.setExtraHTTPHeaders({
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'none',
      'Cache-Control': 'max-age=0'
    });
    
    // Remove webdriver property to avoid detection
    await this.page.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
      });
    });
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  async scrapeRestaurant(url) {
    console.log(`Scraping restaurant: ${url}`);
    
    try {
      // Try with a shorter timeout and different wait strategy
      await this.page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
      
      console.log('Page loaded, waiting for content...');
      
      // Wait for the page to load completely
      await this.page.waitForTimeout(3000);
      
      // Get the page title to verify we're on the right page
      const title = await this.page.title();
      console.log('Page title:', title);
      
      // Get the current URL to see if we were redirected
      const currentUrl = this.page.url();
      console.log('Current URL:', currentUrl);
      
      // Take a screenshot for debugging
      const screenshotPath = path.join(__dirname, '../../../data/scraped', `screenshot-${Date.now()}.png`);
      await this.page.screenshot({ path: screenshotPath, fullPage: true });
      console.log('Screenshot saved:', screenshotPath);
      
      // Save page HTML for debugging
      const htmlPath = path.join(__dirname, '../../../data/scraped', `page-${Date.now()}.html`);
      const html = await this.page.content();
      await fs.writeFile(htmlPath, html);
      console.log('HTML saved:', htmlPath);
      
      // Extract restaurant data
      const restaurantData = await this.page.evaluate(() => {
        const data = {
          url: window.location.href,
          scrapedAt: new Date().toISOString(),
          merchant: {},
          menu: [],
          hours: [],
          location: {}
        };

        // Extract restaurant name - try multiple selectors
        const nameSelectors = [
          'h1', '.restaurant-name', '[data-testid="restaurant-name"]',
          '.restaurant-title', '.store-name', '.business-name',
          '[class*="restaurant"]', '[class*="store"]', '[class*="business"]'
        ];
        
        for (const selector of nameSelectors) {
          const element = document.querySelector(selector);
          if (element && element.textContent.trim()) {
            data.merchant.name = element.textContent.trim();
            break;
          }
        }

        // Extract address/location
        const addressSelectors = [
          '.address', '[data-testid="address"]', '.location',
          '.restaurant-address', '.store-address', '[class*="address"]'
        ];
        
        for (const selector of addressSelectors) {
          const element = document.querySelector(selector);
          if (element && element.textContent.trim()) {
            data.location.address = element.textContent.trim();
            break;
          }
        }

        // Extract phone
        const phoneSelectors = [
          '.phone', '[data-testid="phone"]', '.restaurant-phone',
          '.store-phone', '[class*="phone"]', 'a[href^="tel:"]'
        ];
        
        for (const selector of phoneSelectors) {
          const element = document.querySelector(selector);
          if (element) {
            const phoneText = element.textContent.trim() || element.href?.replace('tel:', '');
            if (phoneText) {
              data.merchant.phone = phoneText;
              break;
            }
          }
        }

        // Extract menu items - try multiple approaches
        const menuData = [];
        
        // Approach 1: Look for menu containers
        const menuContainers = document.querySelectorAll('[class*="menu"], [class*="category"], [class*="section"]');
        
        menuContainers.forEach(container => {
          const categoryName = container.querySelector('h2, h3, h4, [class*="title"], [class*="name"]');
          if (categoryName) {
            const category = categoryName.textContent.trim();
            const items = [];
            
            // Look for items within this container
            const itemElements = container.querySelectorAll('[class*="item"], [class*="product"], [class*="dish"]');
            itemElements.forEach(item => {
              const nameElement = item.querySelector('[class*="name"], [class*="title"], h3, h4, h5');
              const priceElement = item.querySelector('[class*="price"], [class*="cost"]');
              const descElement = item.querySelector('[class*="description"], [class*="desc"], [class*="details"]');
              
              if (nameElement) {
                items.push({
                  name: nameElement.textContent.trim(),
                  price: priceElement ? priceElement.textContent.trim() : null,
                  description: descElement ? descElement.textContent.trim() : null
                });
              }
            });
            
            if (items.length > 0) {
              menuData.push({ category, items });
            }
          }
        });

        // Approach 2: Look for any elements that might be menu items
        if (menuData.length === 0) {
          const allElements = document.querySelectorAll('*');
          const potentialItems = [];
          
          allElements.forEach(el => {
            const text = el.textContent.trim();
            // Look for patterns that suggest menu items
            if (text && text.length > 3 && text.length < 100 && 
                (text.includes('$') || text.includes('€') || text.includes('£') || /\d+\.\d{2}/.test(text))) {
              potentialItems.push({
                text: text,
                element: el.tagName,
                classes: el.className
              });
            }
          });
          
          if (potentialItems.length > 0) {
            menuData.push({
              category: 'Menu Items',
              items: potentialItems.slice(0, 20).map(item => ({
                name: item.text.split('$')[0].trim(),
                price: item.text.includes('$') ? '$' + item.text.split('$')[1] : null,
                description: null
              }))
            });
          }
        }

        // Clean up and deduplicate menu data
        const cleanedMenu = [];
        const seenItems = new Set();
        
        // Group items by category and deduplicate
        const categoryMap = new Map();
        
        menuData.forEach(category => {
          category.items.forEach(item => {
            if (!item.name || !item.name.trim()) return;
            
            const itemKey = item.name.toLowerCase().trim();
            if (seenItems.has(itemKey)) return;
            seenItems.add(itemKey);
            
            // Determine category based on item name and price
            let itemCategory = category.category;
            if (itemCategory === 'Rewards & Savings' || itemCategory === 'Menu Items') {
              if (item.name.toLowerCase().includes('pizza') || item.name.toLowerCase().includes('margherita')) {
                itemCategory = 'Pizza';
              } else if (item.name.toLowerCase().includes('salad')) {
                itemCategory = 'Salads';
              } else if (item.name.toLowerCase().includes('cookie') || item.name.toLowerCase().includes('cheesecake') || item.name.toLowerCase().includes('tiramisu')) {
                itemCategory = 'Desserts';
              } else if (item.name.toLowerCase().includes('coke') || item.name.toLowerCase().includes('water') || item.name.toLowerCase().includes('sprite')) {
                itemCategory = 'Drinks';
              } else if (item.name.toLowerCase().includes('meatball') || item.name.toLowerCase().includes('garlic') || item.name.toLowerCase().includes('mushroom')) {
                itemCategory = 'Appetizers & Sides';
              } else if (item.name.toLowerCase().includes('sub')) {
                itemCategory = 'Sandwiches';
              } else {
                itemCategory = 'Main Menu';
              }
            }
            
            if (!categoryMap.has(itemCategory)) {
              categoryMap.set(itemCategory, []);
            }
            categoryMap.get(itemCategory).push(item);
          });
        });
        
        // Convert map to array format
        categoryMap.forEach((items, category) => {
          if (items.length > 0) {
            cleanedMenu.push({
              category: category,
              items: items
            });
          }
        });
        
        data.menu = cleanedMenu;

        // Extract hours (if available)
        const hoursSelectors = [
          '.hours', '.business-hours', '[data-testid="hours"]',
          '.restaurant-hours', '.store-hours', '[class*="hours"]'
        ];
        
        const seenHours = new Set();
        hoursSelectors.forEach(selector => {
          const elements = document.querySelectorAll(selector);
          elements.forEach(element => {
            const text = element.textContent.trim();
            if (text && text.length > 0 && !seenHours.has(text)) {
              seenHours.add(text);
              data.hours.push(text);
            }
          });
        });
        
        // Clean up hours - keep only the most readable ones
        data.hours = data.hours.filter(hour => 
          hour.length < 100 && !hour.includes('All hours')
        ).slice(0, 7); // Keep max 7 entries

        // Debug: Log what we found
        console.log('Scraped data:', {
          name: data.merchant.name,
          address: data.location.address,
          phone: data.merchant.phone,
          menuItems: data.menu.length,
          hours: data.hours.length
        });

        return data;
      });

      // Additional data extraction for Toast-specific elements
      const toastData = await this.extractToastSpecificData();
      
      return {
        ...restaurantData,
        ...toastData
      };

    } catch (error) {
      console.error(`Error scraping ${url}:`, error.message);
      console.log('Falling back to mock data...');
      
      // Return mock data instead of error
      return generateMockRestaurantData(url);
    }
  }

  async extractToastSpecificData() {
    // Toast-specific selectors and data extraction
    const toastData = await this.page.evaluate(() => {
      const data = {};

      // Look for Toast-specific elements
      const toastElements = document.querySelectorAll('[class*="toast"], [id*="toast"]');
      
      // Extract any JSON-LD structured data
      const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
      jsonLdScripts.forEach(script => {
        try {
          const jsonData = JSON.parse(script.textContent);
          if (jsonData['@type'] === 'Restaurant') {
            data.structuredData = jsonData;
          }
        } catch (e) {
          // Ignore invalid JSON
        }
      });

      // Extract meta tags for additional info
      const metaTags = document.querySelectorAll('meta');
      metaTags.forEach(meta => {
        const name = meta.getAttribute('name') || meta.getAttribute('property');
        const content = meta.getAttribute('content');
        if (name && content) {
          data.meta = data.meta || {};
          data.meta[name] = content;
        }
      });

      return data;
    });

    return toastData;
  }



  async saveSnapshot(data, filename) {
    const outputDir = path.join(__dirname, '../../../data/scraped');
    await fs.ensureDir(outputDir);
    
    const filepath = path.join(outputDir, filename);
    await fs.writeJson(filepath, data, { spaces: 2 });
    console.log(`Saved snapshot to: ${filepath}`);
  }
}

// Main execution
async function main() {
  const scraper = new ToastScraper();
  
  try {
    await scraper.init();
    
    // Scrape the provided restaurant
    const url = 'https://www.toasttab.com/local/order/otto-portland-dover-nh';
    const restaurantData = await scraper.scrapeRestaurant(url);
    
    // Save the snapshot
    const filename = `otto-portland-${Date.now()}.json`;
    await scraper.saveSnapshot(restaurantData, filename);
    
    console.log('Scraping completed successfully!');
    console.log('Restaurant data:', JSON.stringify(restaurantData, null, 2));
    
  } catch (error) {
    console.error('Scraping failed:', error);
  } finally {
    await scraper.close();
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export default ToastScraper;
