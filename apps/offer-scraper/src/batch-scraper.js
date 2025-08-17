import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import ToastScraper from './scraper.js';
import URLLoader from './url-loader.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class BatchScraper {
  constructor() {
    this.urlLoader = new URLLoader();
    this.scraper = null;
    this.results = [];
  }

  async loadConfig() {
    try {
      const config = await this.urlLoader.loadURLs();
      return config;
    } catch (error) {
      console.error('Error loading config:', error.message);
      throw error;
    }
  }

  async init() {
    this.scraper = new ToastScraper();
    await this.scraper.init();
  }

  async close() {
    if (this.scraper) {
      await this.scraper.close();
    }
  }

  async scrapeRestaurant(restaurantConfig) {
    console.log(`\n🍽️  Scraping: ${restaurantConfig.url}`);
    
    try {
      const startTime = Date.now();
      const data = await this.scraper.scrapeRestaurant(restaurantConfig.url);
      const endTime = Date.now();
      
      // Generate ID from URL
      const urlParts = restaurantConfig.url.split('/');
      const urlId = urlParts[urlParts.length - 1];
      const generatedId = urlId.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
      
      // Extract restaurant name from scraped data
      const restaurantName = data.merchant?.name || 'Unknown Restaurant';
      
      // Determine cuisine type from menu items
      const cuisine = this.detectCuisine(data.menu);
      
      // Add auto-generated metadata to scraped data
      const enrichedData = {
        ...data,
        config: {
          id: generatedId,
          name: restaurantName,
          cuisine: cuisine,
          description: `${cuisine} restaurant`,
          location: data.location || {}
        },
        scraping: {
          duration_ms: endTime - startTime,
          timestamp: new Date().toISOString()
        }
      };

      // Save individual restaurant data
      const filename = `${generatedId}-${Date.now()}.json`;
      await this.scraper.saveSnapshot(enrichedData, filename);
      
      this.results.push({
        restaurant: restaurantName,
        success: true,
        filename,
        duration_ms: endTime - startTime,
        menu_items: enrichedData.menu?.reduce((total, category) => total + category.items.length, 0) || 0
      });

      console.log(`✅ Success: ${restaurantName}`);
      console.log(`🏷️  Cuisine: ${cuisine}`);
      console.log(`📋 Menu: ${enrichedData.menu?.length || 0} categories, ${enrichedData.menu?.reduce((total, category) => total + category.items.length, 0) || 0} items`);
      console.log(`⏱️  Duration: ${endTime - startTime}ms`);
      
      return enrichedData;

    } catch (error) {
      console.error(`❌ Failed to scrape ${restaurantConfig.url}:`, error.message);
      
      this.results.push({
        restaurant: restaurantConfig.url,
        success: false,
        error: error.message
      });
      
      return null;
    }
  }

  detectCuisine(menu) {
    if (!menu || !Array.isArray(menu)) return 'unknown';
    
    const menuText = JSON.stringify(menu).toLowerCase();
    
    // Cuisine detection logic
    if (menuText.includes('pizza') || menuText.includes('margherita') || menuText.includes('pepperoni')) {
      return 'pizza';
    }
    if (menuText.includes('lobster') || menuText.includes('seafood') || menuText.includes('clam') || menuText.includes('fish')) {
      return 'seafood';
    }
    if (menuText.includes('bibimbap') || menuText.includes('korean') || menuText.includes('vietnamese') || menuText.includes('thai')) {
      return 'asian';
    }
    if (menuText.includes('taco') || menuText.includes('empanada') || menuText.includes('mexican')) {
      return 'mexican';
    }
    if (menuText.includes('curry') || menuText.includes('indian')) {
      return 'indian';
    }
    if (menuText.includes('burger') || menuText.includes('fries') || menuText.includes('tenders')) {
      return 'american';
    }
    if (menuText.includes('pasta') || menuText.includes('italian')) {
      return 'italian';
    }
    
    return 'american'; // default
  }

  async scrapeAll() {
    try {
      const config = await this.loadConfig();
      console.log(`🚀 Starting batch scrape of ${config.restaurants.length} restaurants`);
      console.log(`⚙️  Config: ${config.scraping.delay_between_requests}ms delay, ${config.scraping.timeout}ms timeout`);
      
      await this.init();
      
      const scrapedData = [];
      
      for (let i = 0; i < config.restaurants.length; i++) {
        const restaurant = config.restaurants[i];
        console.log(`\n📋 [${i + 1}/${config.restaurants.length}] Processing ${restaurant}`);
        
        const data = await this.scrapeRestaurant(restaurant);
        if (data) {
          scrapedData.push(data);
        }
        
        // Add delay between requests (except for the last one)
        if (i < config.restaurants.length - 1) {
          console.log(`⏳ Waiting ${config.scraping.delay_between_requests}ms before next request...`);
          await new Promise(resolve => setTimeout(resolve, config.scraping.delay_between_requests));
        }
      }
      
      // Save batch results summary
      await this.saveBatchResults();
      
      console.log(`\n🎉 Batch scraping completed!`);
      console.log(`📊 Results:`);
      this.results.forEach(result => {
        if (result.success) {
          console.log(`  ✅ ${result.restaurant}: ${result.menu_items} items (${result.duration_ms}ms)`);
        } else {
          console.log(`  ❌ ${result.restaurant}: ${result.error}`);
        }
      });
      
      return scrapedData;
      
    } catch (error) {
      console.error('Batch scraping failed:', error);
      throw error;
    } finally {
      await this.close();
    }
  }

  async saveBatchResults() {
    const batchResults = {
      batch_id: `batch-${Date.now()}`,
      timestamp: new Date().toISOString(),
      total_restaurants: this.results.length,
      successful: this.results.filter(r => r.success).length,
      failed: this.results.filter(r => !r.success).length,
      results: this.results
    };

    const outputDir = path.join(__dirname, '../../../data/scraped');
    await fs.ensureDir(outputDir);
    
    const batchFile = path.join(outputDir, `batch-results-${Date.now()}.json`);
    await fs.writeJson(batchFile, batchResults, { spaces: 2 });
    
    console.log(`📄 Batch results saved to: ${batchFile}`);
  }
}

// Main execution
async function main() {
  const batchScraper = new BatchScraper();
  
  try {
    await batchScraper.scrapeAll();
  } catch (error) {
    console.error('Batch scraping failed:', error);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export default BatchScraper;
