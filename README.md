# Stock Dashboard

A modern web-based stock dashboard application for tracking Indian stock market data with live quotes, interactive charts, and fundamental analysis.

## Features

✓ **Live Stock Data** - Real-time NSE stock prices with automatic fallback to Yahoo Finance  
✓ **10 Top Stocks** - RELIANCE, INFY, HDFCBANK, ICICIBANK, HINDUNILVR, ITC, SBIN, TCS, LT, AXISBANK  
✓ **Interactive Charts** - Intraday candlestick charts with 15-minute intervals  
✓ **Price Filtering** - Filter by minimum and maximum price ranges  
✓ **Trend Filter** - View profits, losses, or all stocks  
✓ **Fundamentals** - P/E ratio, ROE, Debt/Equity, Market Cap, 52W High/Low  
✓ **Responsive UI** - Beautiful dark theme with gradient backgrounds and smooth animations  
✓ **Data Source Tracking** - See whether data comes from NSE or Yahoo Finance  

## Tech Stack

**Backend:**
- Flask 3.0.0 - Python web framework
- yfinance - Stock data from Yahoo Finance
- nsepython - NSE India stock data (optional)
- pandas - Data processing
- requests - HTTP requests

**Frontend:**
- HTML5 - Semantic markup
- CSS3 - Modern responsive design with CSS variables
- JavaScript (Vanilla) - Interactive components
- Chart.js - Data visualization library
- Google Fonts (Manrope) - Typography

## Project Structure

```
stock app 1/
├── app.py                 # Flask backend with API endpoints
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── HOW_TO_RUN.txt        # Terminal execution guide
├── templates/
│   └── index.html        # Main dashboard HTML
└── static/
    ├── style.css         # Dashboard styling
    └── script.js         # Frontend logic and interactivity
```

## Installation

1. **Clone or navigate to project:**
   ```
   cd "C:\Users\Admin\Desktop\stock app 1"
   ```

2. **Create virtual environment** (if not already created):
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

```
.venv/Scripts/python app.py
```

Then open your browser and navigate to:
```
http://127.0.0.1:5000
```

### API Endpoints

**Get Stock List:**
```
GET /get_stocks?min_price=100&max_price=5000&profit=All
```

**Get Chart Data:**
```
GET /get_chart/RELIANCE
```

**Get Fundamentals:**
```
GET /get_fundamentals/RELIANCE
```

## Features Explained

### Stock List
- Click any stock to view its intraday chart and fundamentals
- Price column shows current stock price in INR
- Change column displays price movement and percentage change
- Green text = profit (price up), Red text = loss (price down)

### Filters
- **Min Price / Max Price:** Filter stocks within a price range
- **Trend:** View only profitable, loss-making, or all stocks
- **Apply Filter:** Click to update the stock list

### Chart
- 15-minute interval intraday chart
- Shows price movement throughout the trading day
- Smooth line chart with gradient fill

### Fundamentals
- **P/E Ratio:** Price-to-earnings ratio
- **ROE:** Return on equity
- **Debt/Equity:** Leverage ratio
- **Market Cap:** Market capitalization
- **52W High/Low:** 52-week high and low prices
- **Data Source:** Shows NSE or Yahoo Finance as the data provider

## Data Sources

### Primary: NSE (National Stock Exchange)
- Live Indian stock market data
- Accurate for NSE-listed companies

### Fallback: Yahoo Finance
- Used when NSE data is unavailable
- Global stock market data
- Reliable and widely used

## Browser Compatibility

✓ Chrome/Chromium  
✓ Firefox  
✓ Safari  
✓ Edge  

## Troubleshooting

**Port 5000 already in use:**
```
# Kill the process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Module not found errors:**
```
pip install -r requirements.txt
```

**No stocks displaying:**
- Check internet connection
- Verify NSE/Yahoo Finance are accessible
- Check browser console for errors (F12)

## Performance Tips

1. **First load** may take 5-10 seconds as stock data is fetched
2. **Filtering** is instant (processed on client-side)
3. **Charts** load on demand when you click a stock
4. **Fundamentals** update whenever stock is selected

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Search functionality
- [ ] Stock comparison charts
- [ ] Portfolio tracking
- [ ] Price alerts
- [ ] Historical data export
- [ ] Dark/Light theme toggle

## License

Open source project - Free to use and modify

## Support

For issues or suggestions, check the terminal output for error messages.

---

**Version:** 1.0  
**Created:** April 2026  
**Status:** Production Ready ✓
