document.addEventListener('DOMContentLoaded', function() {
    const asset = document.getElementById("asset").textContent
    let symbol;
    
    if (asset === "XAUUSD"){
        symbol = "FX_IDC:XAUUSD";
    }else{
        symbol = `FX:${asset.slice(0, -1)}`;
    }
    
    new TradingView.widget({
        "container_id": "forex-chart", // Match this ID with your div
        "width": "100%", // Full width
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


const quill = new Quill('#editor', {
    theme: 'snow'
});

const pnl = document.getElementById("pnl")
const pnlProperty = document.getElementById("property")
const value = parseFloat(pnl.textContent.replace(/[^0-9.-]+/g, ""));
if (value > 0){
    pnl.style.color = "rgb(1, 149, 1)"
} else {
    pnl.style.color = "red"
    pnlProperty.style.color = "red"

}


document.getElementById("quill-form").onsubmit = function(){
    let quillHtmlContent = quill.root.innerHTML;
    
    let tempElement = document.createElement("div");
    tempElement.innerHTML = quillHtmlContent;

    // Extract plain text (without HTML tags)
    let plainText = tempElement.textContent || tempElement.innerText;

    // Assign plain text to the hidden input for form submission
    let quillContentInput = document.querySelector("input[name=quill_content]");
    quillContentInput.value = plainText;
    
}