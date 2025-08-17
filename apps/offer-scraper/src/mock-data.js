// Mock data generator for restaurant scraping when Cloudflare blocks access
export function generateMockRestaurantData(url) {
  const urlParts = url.split('/');
  const restaurantName = urlParts[urlParts.length - 1]?.replace(/-/g, ' ') || 'Restaurant';
  
  return {
    url,
    scrapedAt: new Date().toISOString(),
    merchant: {
      name: restaurantName.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
      phone: '+1 (555) 123-4567',
      domain: 'order.example.com'
    },
    location: {
      address: '123 Main Street, Portland, NH 03820',
      lat: 43.1939,
      lng: -70.8737,
      city: 'Portland',
      state: 'NH',
      country: 'US'
    },
    menu: [
      {
        category: 'Appetizers',
        items: [
          { name: 'Bruschetta', price: '$8.50', description: 'Toasted bread with fresh tomatoes, basil, and mozzarella' },
          { name: 'Calamari', price: '$12.00', description: 'Crispy fried squid with marinara sauce' },
          { name: 'Garlic Bread', price: '$6.00', description: 'Fresh baked bread with garlic butter and herbs' }
        ]
      },
      {
        category: 'Pizza',
        items: [
          { name: 'Margherita', price: '$16.00', description: 'Fresh mozzarella, tomato sauce, and basil' },
          { name: 'Pepperoni', price: '$18.00', description: 'Classic pepperoni with mozzarella and tomato sauce' },
          { name: 'Vegetarian', price: '$17.00', description: 'Bell peppers, mushrooms, onions, and olives' },
          { name: 'BBQ Chicken', price: '$19.00', description: 'BBQ sauce, grilled chicken, red onions, and cilantro' }
        ]
      },
      {
        category: 'Pasta',
        items: [
          { name: 'Spaghetti Marinara', price: '$14.00', description: 'Classic tomato sauce with fresh herbs' },
          { name: 'Fettuccine Alfredo', price: '$16.00', description: 'Creamy parmesan sauce with garlic' },
          { name: 'Penne Arrabbiata', price: '$15.00', description: 'Spicy tomato sauce with red pepper flakes' }
        ]
      },
      {
        category: 'Salads',
        items: [
          { name: 'Caesar Salad', price: '$10.00', description: 'Romaine lettuce, parmesan, croutons, and caesar dressing' },
          { name: 'Greek Salad', price: '$11.00', description: 'Mixed greens, feta, olives, tomatoes, and cucumber' }
        ]
      },
      {
        category: 'Desserts',
        items: [
          { name: 'Tiramisu', price: '$8.00', description: 'Classic Italian dessert with coffee and mascarpone' },
          { name: 'Chocolate Lava Cake', price: '$9.00', description: 'Warm chocolate cake with molten center' }
        ]
      }
    ],
    hours: [
      'Monday: 11:00 AM - 10:00 PM',
      'Tuesday: 11:00 AM - 10:00 PM', 
      'Wednesday: 11:00 AM - 10:00 PM',
      'Thursday: 11:00 AM - 10:00 PM',
      'Friday: 11:00 AM - 11:00 PM',
      'Saturday: 11:00 AM - 11:00 PM',
      'Sunday: 12:00 PM - 9:00 PM'
    ],
    meta: {
      description: 'Authentic Italian cuisine in the heart of Portland',
      keywords: 'pizza, pasta, italian, restaurant, portland'
    }
  };
}

export function generateMockOSF(merchantId, merchantName, domain) {
  return {
    osf_version: "0.1",
    publisher: {
      merchant_id: merchantId,
      name: merchantName,
      domain: domain
    },
    updated_at: new Date().toISOString(),
    offers: [
      {
        href: `https://${domain}/.well-known/offers/ofr_001.json`,
        offer_id: "ofr_001",
        updated_at: new Date().toISOString()
      },
      {
        href: `https://${domain}/.well-known/offers/ofr_002.json`,
        offer_id: "ofr_002", 
        updated_at: new Date().toISOString()
      }
    ]
  };
}

export function generateMockOfferDocument(offerId, merchantData) {
  return {
    offer_id: offerId,
    merchant: {
      id: merchantData.merchant.id || "toast_" + merchantData.merchant.name.toLowerCase().replace(/\s+/g, '_'),
      name: merchantData.merchant.name,
      domain: merchantData.merchant.domain,
      location: {
        lat: merchantData.location.lat,
        lng: merchantData.location.lng,
        city: merchantData.location.city,
        country: merchantData.location.country
      }
    },
    terms: {
      trigger: "checkout_complete",
      bounty: {
        currency: "USD",
        amount: 2.50,
        rev_share_split: {
          user: 0.5,
          agent: 0.4,
          associate: 0.1
        }
      },
      eligibility: ["US-NH"],
      sku_scope: ["menu:*"],
      schedule: {
        days: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        local_time: {
          start: "11:00",
          end: "22:00"
        }
      },
      expiration: "2026-12-31T23:59:59Z"
    },
    attribution: {
      method: "server_postback",
      postback_url: "http://localhost:3001/postbacks",
      required_fields: ["order_id", "agent_id", "signature", "timestamp"],
      signature_alg: "ed25519"
    },
    provenance: {
      publisher: "merchant_first_party",
      published_at: new Date().toISOString(),
      signature: "base64-edsig-demo-signature"
    },
    labels: ["pizza", "pasta", "italian", "dinner"],
    geo: {
      radius_m: 16000
    }
  };
}
