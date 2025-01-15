// Initialize chart and candle series
const chart = LightweightCharts.createChart(document.getElementById('chart'), {
    width: 1335,
    height: 700,
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
    crosshair: {
      mode: LightweightCharts.CrosshairMode.Normal,
    },
    rightPriceScale: {
      borderVisible: false,
    },
    timeScale: {
      borderVisible: false,
      timeVisible: true,  // Show time
      secondsVisible: true,
      tickMarkFormatter: function(time) {
        const date = new Date(time * 1000); // Convert time to milliseconds
        const dayOfWeek = date.toLocaleString('en-US', { weekday: 'short' }); // Get short weekday name
        const timeString = date.toLocaleString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

        // Combine day of the week, time, and date
        return `${dayOfWeek} ${timeString}`;
      },
    },
});


const candleSeries = chart.addCandlestickSeries({
    priceFormat: {
        type: 'price',
        precision: 5,     // Number of decimal places for displayed prices
        minMove: 0.00001  // Smallest price change
    },
    upColor: '#4357e8',        // Color for candlesticks where the close > open (bullish)
    borderUpColor: '#4357e8',  // Border color for bullish candlesticks
    wickUpColor: '#4357e8',    // Wick color for bullish candlesticks
    downColor: '#797777',      // Color for candlesticks where the close < open (bearish)
    borderDownColor: '#797777',// Border color for bearish candlesticks
    wickDownColor: '#797777',  // Wick color for bearish candlesticks
    borderVisible: true,       // Show borders for the candlesticks
    wickVisible: true,         // Show wicks for the candlesticks
    
});

// Function to load historical data from the backend
async function loadHistoricalData() {
    try {
        const response = await fetch('fetch-historical-data/');
        const responseData = await response.json();

        const instrument = responseData.instrument; // "GBPUSDm"
        const timeframe = responseData.timeframe;
        
        // Format data for Lightweight Charts
        const chartData = responseData.data.map(item => ({
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

  