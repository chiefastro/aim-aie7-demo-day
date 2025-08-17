import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class URLLoader {
  constructor() {
    this.textPath = path.join(__dirname, '../config/restaurants.txt');
  }

  async loadURLs() {
    // Use text file (simpler interface)
    if (await fs.pathExists(this.textPath)) {
      return this.loadFromTextFile();
    }
    
    throw new Error('No restaurant configuration found. Please create config/restaurants.txt with one URL per line');
  }

  async loadFromTextFile() {
    const content = await fs.readFile(this.textPath, 'utf8');
    const lines = content.split('\n');
    
    const urls = [];
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        urls.push({ url: trimmed });
      }
    }
    
    console.log(`📄 Loaded ${urls.length} URLs from text file`);
    return {
      restaurants: urls,
      scraping: {
        delay_between_requests: 2000,
        timeout: 15000,
        max_retries: 3,
        headless: false
      }
    };
  }



  async saveURLsToTextFile(urls) {
    const content = urls.map(url => url.url).join('\n');
    await fs.writeFile(this.textPath, content);
    console.log(`💾 Saved ${urls.length} URLs to text file`);
  }

  async addURL(url) {
    const config = await this.loadURLs();
    config.restaurants.push({ url });
    await this.saveURLsToTextFile(config.restaurants);
    return config;
  }
}

export default URLLoader;
