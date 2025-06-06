let tradeElements = document.querySelectorAll(".trade");

tradeElements.forEach(tradeElement => {
    let profitText = tradeElement.querySelector(".first").textContent;
    const profitValue = parseFloat(profitText.replace(/[^0-9.-]+/g, ""));

    if (profitValue > 0) {
        tradeElement.style.borderColor = "#182739";
        tradeElement.querySelector(".bar").style.backgroundColor = "greenyellow"
    } else {
        tradeElement.style.borderColor = "#182739"; 
        tradeElement.querySelector(".bar").style.backgroundColor = "#676767"
    }

    tradeElement.addEventListener("mouseover", () => {
        if (profitValue > 0) {
            tradeElement.style.backgroundColor = "#DFEFDA"; // Light green background on hover for profit
        } else {
            tradeElement.style.backgroundColor = "#999999"; // Light red background on hover for loss
        }
        tradeElement.style.color = "black";
    });

    // Remove hover effect: on mouse out
    tradeElement.addEventListener("mouseout", () => {
        tradeElement.style.backgroundColor = ""; // Reset background to default on hover out
        tradeElement.style.color = "";
    });

    tradeElement.addEventListener("click", () => {
        let tradeID = tradeElement.querySelector(".heads h2").textContent.match(/\d+/)[0];
        console.log(tradeID)
        window.location.href = `journal/${tradeID}`
    })
})