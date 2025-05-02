document.addEventListener('DOMContentLoaded', function() {
    const asset = document.getElementById("asset").textContent
    let symbol;
    
    
    if (asset === "XAUUSD"){
        console.log(asset)
        symbol = "FX_IDC:XAUUSD";
    }else if (asset === "US30.cash"){
        console.log(asset)
        symbol = "OANDA:US30USD";
    } else {
        console.log(asset)
        symbol = `FX:${asset.slice(0, -1)}`;
        console.log("I'm here")
    }
    
    new TradingView.widget({
        "container_id": "forex-chart", // Match this ID with your div
        "width": "110%", // Full width
        "height": "50rem", // Full height
        "symbol": symbol, // Example symbol
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "withdateranges": true,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "details": true,
        "hotlist": true,
        "calendar": true,
        "studies": [],
        "container": "forex-chart"
    }); 
});

