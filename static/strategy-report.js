function centerText(firstLine, secondLine){
    return {
        id: 'centerText',
        beforeDraw: function(chart) {
            const {width, height, ctx} = chart;
            ctx.restore();
    
            // Set font properties for the first line (bold "12")
            let fontSize = (height / 100).toFixed(2);  // Adjust size as needed
            ctx.font = `bold ${fontSize}em Arial`;  // Bold font for "12"
            ctx.fillStyle = "#000000";  // White color
            ctx.textBaseline = "middle";
            ctx.textAlign = "center";
    
            // Draw the first line of text
            const text1 = `${firstLine}`;
            const textX = width / 2;
            const textY = height / 2 - 10;  // Adjust Y position to move it slightly up
            ctx.fillText(text1, textX, textY);
    
            // Set font properties for the second line (regular "solid trades")
            fontSize = (height / 200).toFixed(2);  // Smaller font size for "solid trades"
            ctx.font = `${fontSize}em Arial`;
            ctx.fillStyle = "#000000";  // White color
    
            // Draw the second line of text
            const text2 = `${secondLine}`;
            const textY2 = height / 2 + 20;  // Adjust Y position to place it under "12"
            ctx.fillText(text2, textX, textY2);
    
            ctx.save();
        }
    };    
}














const charts = document.querySelectorAll(".first-doughnut")

new Chart(charts, {
    type: "doughnut",
    data: {
        labels: ["Wins", "losses"],
        datasets: [{
            label: "Trades",
            data: [9, 5],
            backgroundColor: [
                "#6dc407",
                "#7f8c8d"
            ],
            borderWidth: 0,
        }]
    },
    options: {
        cutout: "60%",
        plugins: {
            legend: {
                display: false
            }
        }
    },
    plugins: [centerText("23", "Total Trades")]
})



const secondChart = document.querySelectorAll(".second-doughnut");

new Chart(secondChart, {
    type: "doughnut",
    data:{
        labels: ["long", "short"],
        datasets: [{
            label: "trades",
            data: [7, 9],
            backgroundColor: [
                "#6dc407",
                "#7f8c8d"
            ],
            borderWidth: 0,
        }]
    },
    options:{
        cutout: "60%",
        plugins:{
            legend:{
                display: false
            }
        }
    },
    plugins: [centerText("only", "Winning trades")]
})