// Initialize chart and candle series
const chart = LightweightCharts.createChart(document.getElementById('chart'), {
    width: 600,
    height: 400,
    layout: {
      backgroundColor: '#FFFFFF',
      textColor: '#000',
    },
    grid: {
      vertLines: {
        color: '#eee',
      },
      horzLines: {
        color: '#eee',
      },
    },
    rightPriceScale: {
      borderVisible: false,
    },
    timeScale: {
      borderVisible: false,
    },
});

const candleSeries = chart.addCandlestickSeries({
    priceFormat: {
        type: 'price',
        precision: 5,     // Number of decimal places for displayed prices
        minMove: 0.00001  // Smallest price change
    }
});

// Function to load historical data from the backend
async function loadHistoricalData() {
    try {
        const response = await fetch('fetch-historical-data/');
        const data = await response.json();
        
        // Format data for Lightweight Charts
        const chartData = data.map(item => ({
            time: new Date(item.time).getTime(),  // Convert to seconds timestamp
            open: item.open,
            high: item.high,
            low: item.low,
            close: item.close
        }));
        
        // Set data to the candlestick series
        candleSeries.setData(chartData);
    } catch (error) {
        console.error('Error loading historical data:', error);
    }
}

// Call the function to load data on page load or chart initialization
loadHistoricalData();

  