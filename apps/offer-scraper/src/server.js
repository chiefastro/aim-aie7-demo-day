import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs-extra';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from the OSF directory
const osfDir = path.join(__dirname, '../../../data/osf');
app.use('/osf', express.static(osfDir));

// Add CORS headers for demo purposes
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// List available merchants
app.get('/merchants', async (req, res) => {
  try {
    const merchants = await fs.readdir(osfDir);
    const merchantList = merchants.map(merchant => ({
      id: merchant,
      osf_url: `http://localhost:${PORT}/osf/${merchant}/.well-known/osf.json`
    }));
    
    res.json({
      merchants: merchantList,
      total: merchantList.length
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Serve the main OSF endpoint for a merchant
app.get('/merchant/:merchantId/osf', async (req, res) => {
  const { merchantId } = req.params;
  const osfPath = path.join(osfDir, merchantId, '.well-known/osf.json');
  
  try {
    if (await fs.pathExists(osfPath)) {
      const osf = await fs.readJson(osfPath);
      res.json(osf);
    } else {
      res.status(404).json({ error: 'OSF not found for merchant' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Serve individual offer documents
app.get('/merchant/:merchantId/offer/:offerId', async (req, res) => {
  const { merchantId, offerId } = req.params;
  const offerPath = path.join(osfDir, merchantId, '.well-known/offers', `${offerId}.json`);
  
  try {
    if (await fs.pathExists(offerPath)) {
      const offer = await fs.readJson(offerPath);
      res.json(offer);
    } else {
      res.status(404).json({ error: 'Offer not found' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Demo endpoint to show the ACP structure
app.get('/demo', (req, res) => {
  res.json({
    message: 'ACP Demo Server',
    endpoints: {
      health: `http://localhost:${PORT}/health`,
      merchants: `http://localhost:${PORT}/merchants`,
      merchant_osf: `http://localhost:${PORT}/merchant/{merchantId}/osf`,
      merchant_offer: `http://localhost:${PORT}/merchant/{merchantId}/offer/{offerId}`,
      static_files: `http://localhost:${PORT}/osf/{merchantId}/.well-known/osf.json`
    },
    example: {
      osf: `http://localhost:${PORT}/osf/toast_otto_portland_dover_nh/.well-known/osf.json`,
      offer: `http://localhost:${PORT}/osf/toast_otto_portland_dover_nh/.well-known/offers/ofr_001.json`
    }
  });
});

app.listen(PORT, () => {
  console.log(`ACP Demo Server running on http://localhost:${PORT}`);
  console.log(`Demo info: http://localhost:${PORT}/demo`);
  console.log(`Available merchants: http://localhost:${PORT}/merchants`);
});
