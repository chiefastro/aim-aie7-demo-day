import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { generateMockOSF } from './mock-data.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class ACPGenerator {
  constructor() {
    this.outputDir = path.join(__dirname, '../../../data/osf');
  }

  async ensureOutputDir() {
    await fs.ensureDir(this.outputDir);
  }

  // Geocoding data for the restaurants
  getGeocodingData(restaurantData) {
    const geocodingMap = {
      'otto_portland_dover_nh': {
        lat: 43.1979,
        lng: -70.8737,
        formatted_address: '431 Central Avenue, Dover, NH 03820'
      },
      'street_exeter_8_clifford_street_cmaxy': {
        lat: 42.9814,
        lng: -70.9478,
        formatted_address: '8 Clifford Street, Exeter, NH 03833'
      },
      'newicks_lobster_house_dover_431_dover_point_rd': {
        lat: 43.1587,
        lng: -70.8234,
        formatted_address: '431 Dover Point Rd, Dover, NH 03820'
      }
    };

    const merchantId = restaurantData.config?.id || 
      `toast_${restaurantData.merchant.name.toLowerCase().replace(/\s+/g, '_')}`;
    
    return geocodingMap[merchantId] || {
      lat: 43.1979,
      lng: -70.8737,
      formatted_address: restaurantData.location?.address || 'Dover, NH'
    };
  }

  // Generate rich restaurant description for embedding
  generateRestaurantDescription(restaurantData) {
    const menu = restaurantData.menu || [];
    const allItems = menu.flatMap(category => category.items || []);
    
    // Extract key menu items for description
    const popularItems = allItems
      .filter(item => item.price && parseFloat(item.price.replace('$', '')) > 10)
      .slice(0, 8)
      .map(item => item.name);
    
    const cuisine = this.detectCuisineFromMenu(allItems);
    const hours = restaurantData.hours?.[0] || '11:00 AM - 10:00 PM';
    
    return `${restaurantData.merchant.name} is a ${cuisine} restaurant serving ${popularItems.join(', ')} and more. Open ${hours}. Located in ${restaurantData.location?.address || 'Dover, NH'}.`;
  }

  // Detect cuisine type from menu items
  detectCuisineFromMenu(menuItems) {
    const menuText = menuItems.map(item => item.name).join(' ').toLowerCase();
    
    if (menuText.includes('pizza') || menuText.includes('margherita') || menuText.includes('pepperoni')) {
      return 'Italian pizza';
    }
    if (menuText.includes('lobster') || menuText.includes('clam') || menuText.includes('haddock') || menuText.includes('scallop')) {
      return 'seafood';
    }
    if (menuText.includes('bibimbap') || menuText.includes('curry') || menuText.includes('taco') || menuText.includes('burrito')) {
      return 'international fusion';
    }
    if (menuText.includes('burger') || menuText.includes('sandwich')) {
      return 'American';
    }
    
    return 'casual dining';
  }

  // Generate menu item descriptions for embedding
  generateMenuItemDescriptions(menuItems, maxItems = 5) {
    return menuItems
      .filter(item => item.price && parseFloat(item.price.replace('$', '')) > 8)
      .slice(0, maxItems)
      .map(item => `${item.name} - ${item.price}`);
  }

  // Generate realistic offer based on menu data
  generateRealisticOffer(offerId, restaurantData, offerType = 'lunch') {
    const menu = restaurantData.menu || [];
    const allItems = menu.flatMap(category => category.items || []);
    const geocoding = this.getGeocodingData(restaurantData);
    
    // Select featured menu items based on offer type
    let featuredItems = [];
    let minSpend = 0;
    let description = '';
    
    if (offerType === 'lunch') {
      const lunchItems = allItems.filter(item => 
        item.price && parseFloat(item.price.replace('$', '')) <= 20 &&
        (item.name.toLowerCase().includes('lunch') || 
         item.name.toLowerCase().includes('sandwich') ||
         item.name.toLowerCase().includes('salad') ||
         item.name.toLowerCase().includes('pizza'))
      );
      featuredItems = lunchItems.slice(0, 3);
      minSpend = 15;
      description = `Lunch special at ${restaurantData.merchant.name}. Get $2.50 back when you spend $${minSpend} or more on lunch items.`;
    } else {
      const dinnerItems = allItems.filter(item => 
        item.price && parseFloat(item.price.replace('$', '')) > 15 &&
        !item.name.toLowerCase().includes('lunch')
      );
      featuredItems = dinnerItems.slice(0, 3);
      minSpend = 25;
      description = `Dinner offer at ${restaurantData.merchant.name}. Get $2.50 back when you spend $${minSpend} or more on dinner entrees.`;
    }

    const restaurantDescription = this.generateRestaurantDescription(restaurantData);
    const menuDescriptions = this.generateMenuItemDescriptions(featuredItems);
    
    return {
      offer_id: offerId,
      offer_version: "1.0",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days
      
      title: `${restaurantData.merchant.name} ${offerType.charAt(0).toUpperCase() + offerType.slice(1)} Offer`,
      description: description,
      
      // Rich content for embedding
      content: {
        restaurant_description: restaurantDescription,
        featured_items: menuDescriptions,
        cuisine_type: this.detectCuisineFromMenu(allItems),
        price_range: this.getPriceRange(allItems),
        dietary_options: this.getDietaryOptions(allItems)
      },
      
      terms: {
        min_spend: minSpend,
        max_discount: 2.50,
        valid_days: ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
        valid_hours: {
          start: "11:00",
          end: "22:00"
        },
        restrictions: [
          "Valid for dine-in and takeout orders",
          "Cannot be combined with other offers",
          "Valid only at this location"
        ]
      },
      
      bounty: {
        amount: 2.50,
        currency: "USD",
        revenue_split: {
          consumer: 50,
          merchant: 40,
          platform: 10
        }
      },
      
      merchant: {
        id: restaurantData.config?.id || `toast_${restaurantData.merchant.name.toLowerCase().replace(/\s+/g, '_')}`,
        name: restaurantData.merchant.name,
        location: {
          lat: geocoding.lat,
          lng: geocoding.lng,
          address: geocoding.formatted_address,
          city: "Dover",
          state: "NH",
          zip: "03820"
        },
        phone: restaurantData.merchant.phone || "Call",
        hours: restaurantData.hours || ["11:00 am - 10:00 pm"]
      },
      
      attribution: {
        method: "receipt_upload",
        instructions: "Upload your receipt after dining to receive your bounty",
        required_fields: ["total_amount", "date", "items"]
      },
      
      provenance: {
        source: "merchant_direct",
        verified: true,
        last_verified: new Date().toISOString()
      },
      
      labels: this.generateLabelsFromMenu(allItems, offerType),
      
      // Search metadata
      search_metadata: {
        cuisine: this.detectCuisineFromMenu(allItems),
        price_range: this.getPriceRange(allItems),
        location: {
          city: "Dover",
          state: "NH",
          coordinates: [geocoding.lng, geocoding.lat] // GeoJSON format for Qdrant
        },
        meal_type: offerType,
        dietary_restrictions: this.getDietaryOptions(allItems),
        popular_items: featuredItems.map(item => item.name)
      }
    };
  }

  getPriceRange(menuItems) {
    const prices = menuItems
      .filter(item => item.price)
      .map(item => parseFloat(item.price.replace('$', '')))
      .filter(price => !isNaN(price));
    
    if (prices.length === 0) return "$$";
    
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    
    if (max <= 15) return "$";
    if (max <= 30) return "$$";
    if (max <= 60) return "$$$";
    return "$$$$";
  }

  getDietaryOptions(menuItems) {
    const options = [];
    const menuText = menuItems.map(item => item.name).join(' ').toLowerCase();
    
    if (menuText.includes('veggie') || menuText.includes('vegetable')) options.push('vegetarian');
    if (menuText.includes('gluten-free') || menuText.includes('gf')) options.push('gluten-free');
    if (menuText.includes('seafood') || menuText.includes('fish')) options.push('seafood');
    
    return options;
  }

  generateLabelsFromMenu(menuItems, offerType) {
    const labels = new Set();
    const menuText = menuItems.map(item => item.name).join(' ').toLowerCase();
    
    // Cuisine labels
    if (menuText.includes('pizza')) labels.add('pizza');
    if (menuText.includes('pasta')) labels.add('pasta');
    if (menuText.includes('salad')) labels.add('salad');
    if (menuText.includes('burger')) labels.add('burger');
    if (menuText.includes('sushi')) labels.add('sushi');
    if (menuText.includes('taco')) labels.add('mexican');
    if (menuText.includes('curry')) labels.add('indian');
    if (menuText.includes('bibimbap')) labels.add('korean');
    if (menuText.includes('lobster') || menuText.includes('clam') || menuText.includes('haddock')) {
      labels.add('seafood');
      labels.add('lobster');
      labels.add('fish');
    }
    
    // Meal type labels
    labels.add(offerType);
    if (offerType === 'lunch') {
      labels.add('lunch');
      labels.add('midday');
    } else {
      labels.add('dinner');
      labels.add('evening');
    }
    
    // Service labels
    labels.add('dine-in');
    labels.add('takeout');
    
    // Location labels
    labels.add('dover-nh');
    labels.add('new-hampshire');
    labels.add('seacoast');
    
    return Array.from(labels);
  }

  generateOSF(restaurantData) {
    const merchantId = restaurantData.config?.id || 
      `toast_${restaurantData.merchant.name.toLowerCase().replace(/\s+/g, '_')}`;
    
    return {
      osf_version: "0.1",
      publisher: {
        merchant_id: merchantId,
        name: restaurantData.merchant.name,
        domain: "localhost:3000"
      },
      updated_at: new Date().toISOString(),
      offers: [
        {
          href: `http://localhost:3000/osf/${merchantId}/.well-known/offers/ofr_001.json`,
          offer_id: "ofr_001",
          updated_at: new Date().toISOString()
        },
        {
          href: `http://localhost:3000/osf/${merchantId}/.well-known/offers/ofr_002.json`,
          offer_id: "ofr_002",
          updated_at: new Date().toISOString()
        }
      ]
    };
  }

  async generateACPFromRestaurantData(restaurantData) {
    await this.ensureOutputDir();
    
    const merchantId = restaurantData.config?.id || 
      `toast_${restaurantData.merchant.name.toLowerCase().replace(/\s+/g, '_')}`;
    
    // Generate OSF
    const osf = this.generateOSF(restaurantData);
    
    // Generate realistic offer documents
    const lunchOffer = this.generateRealisticOffer('ofr_001', restaurantData, 'lunch');
    const dinnerOffer = this.generateRealisticOffer('ofr_002', restaurantData, 'dinner');
    
    // Create merchant directory
    const merchantDir = path.join(this.outputDir, merchantId);
    await fs.ensureDir(merchantDir);
    await fs.ensureDir(path.join(merchantDir, '.well-known'));
    await fs.ensureDir(path.join(merchantDir, '.well-known/offers'));
    
    // Save OSF
    const osfPath = path.join(merchantDir, '.well-known/osf.json');
    await fs.writeJson(osfPath, osf, { spaces: 2 });
    
    // Save offer documents
    const lunchOfferPath = path.join(merchantDir, '.well-known/offers/ofr_001.json');
    const dinnerOfferPath = path.join(merchantDir, '.well-known/offers/ofr_002.json');
    
    await fs.writeJson(lunchOfferPath, lunchOffer, { spaces: 2 });
    await fs.writeJson(dinnerOfferPath, dinnerOffer, { spaces: 2 });
    
    console.log(`Generated ACP documents for ${restaurantData.merchant.name}:`);
    console.log(`  OSF: ${osfPath}`);
    console.log(`  Lunch Offer: ${lunchOfferPath}`);
    console.log(`  Dinner Offer: ${dinnerOfferPath}`);
    console.log(`  Featured Items: ${lunchOffer.content.featured_items.join(', ')}`);
    console.log(`  Location: ${lunchOffer.merchant.location.address}`);
    console.log(`  Coordinates: ${lunchOffer.merchant.location.lat}, ${lunchOffer.merchant.location.lng}`);
    
    return {
      osf,
      offers: [lunchOffer, dinnerOffer],
      paths: {
        osf: osfPath,
        offers: [lunchOfferPath, dinnerOfferPath]
      }
    };
  }

  async generateFromScrapedData() {
    const scrapedDir = path.join(__dirname, '../../../data/scraped');
    
    if (!await fs.pathExists(scrapedDir)) {
      console.log('No scraped data found. Please run the scraper first.');
      return;
    }
    
    const files = await fs.readdir(scrapedDir);
    const jsonFiles = files.filter(f => f.endsWith('.json') && !f.startsWith('batch-results'));
    
    console.log(`Found ${jsonFiles.length} scraped restaurant files`);
    
    for (const file of jsonFiles) {
      const filePath = path.join(scrapedDir, file);
      const restaurantData = await fs.readJson(filePath);
      
      if (restaurantData.error) {
        console.log(`Skipping ${file} due to error: ${restaurantData.error}`);
        continue;
      }
      
      await this.generateACPFromRestaurantData(restaurantData);
    }
  }
}

// Main execution
async function main() {
  const generator = new ACPGenerator();
  
  try {
    await generator.generateFromScrapedData();
    console.log('ACP generation completed successfully!');
  } catch (error) {
    console.error('ACP generation failed:', error);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export default ACPGenerator;
