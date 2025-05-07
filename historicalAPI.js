const express = require("express");
const { NseIndia } = require("stock-nse-india");
const cors = require("cors");

const app = express();
const port = 3000;
const nseIndia = new NseIndia();

app.use(cors()); // Enable CORS for frontend access

// GET /historical?symbol=TCS&from=01-05-2024
app.get("/historical", async (req, res) => {
  const symbol = req.query.symbol;
  const startDate = req.query.from;
  const endDate = "01-01-2025"; // ✅ Fixed

  if (!symbol || !startDate) {
    return res.status(400).json({ error: "Missing 'symbol' or 'from' query parameters." });
  }

  try {
    console.log(`⏳ Fetching historical data for ${symbol} from ${startDate} to ${endDate}...`);

    const endpoint = `/api/historical/cm/equity?symbol=${symbol.toUpperCase()}&series=[%22EQ%22]&from=${startDate}&to=${endDate}`;
    const response = await nseIndia.getDataByEndpoint(endpoint);

    if (!response?.data || response.data.length === 0) {
      return res.status(404).json({ error: "⚠️ No historical data found for this symbol and date range." });
    }

    return res.json({ data: response.data });
  } catch (error) {
    console.error("❌ Error:", error.message);
    return res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`🚀 API server running at http://localhost:${port}/historical`);
});
