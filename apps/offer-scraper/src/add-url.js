import URLLoader from './url-loader.js';

async function main() {
  const url = process.argv[2];
  
  if (!url) {
    console.log('Usage: node add-url.js <restaurant-url>');
    console.log('');
    console.log('Example:');
    console.log('  node add-url.js https://www.toasttab.com/local/order/restaurant-name');
    console.log('');
    console.log('Or just edit config/restaurants.txt directly with one URL per line');
    process.exit(1);
  }

  try {
    const urlLoader = new URLLoader();
    const config = await urlLoader.addURL(url);
    
    console.log(`✅ Added URL: ${url}`);
    console.log(`📄 Total URLs: ${config.restaurants.length}`);
    console.log('');
    console.log('To scrape all restaurants: npm run batch-scrape');
    
  } catch (error) {
    console.error('❌ Error adding URL:', error.message);
    process.exit(1);
  }
}

main();
