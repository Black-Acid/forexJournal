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
            data: [window.profitableTrades, window.losingTrades],
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
    plugins: [centerText(`${window.totalTrades}`, "Total Trades")]
})



const secondChart = document.querySelectorAll(".second-doughnut");

new Chart(secondChart, {
    type: "doughnut",
    data:{
        labels: ["long", "short"],
        datasets: [{
            label: "trades",
            data: [window.winBuys, window.winSells],
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
    plugins: [centerText("Only", "Winning trades")]
})


const barChart = document.querySelector(".bar-canvas")

new Chart(barChart, {
    type: "bar",
    data:{
        labels: window.symbolData,
        datasets: [{
            label: "PnL",
            data: window.symbolValues,
            backgroundColor: function(context){
                const value = context.raw;
                return value >= 0 ? "#6dc407" : "#7f8c8d"
            },
            borderColor: function(context){
                const value = context.raw;
                return value >= 0 ? "#6dc407" : "#7f8c8d"
            },
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                barPercentage: 0.5,
                categoryPercentage: 0.7
            },
            y: {
                beginAtZero: true
            }
        }
    }
})


// const tradeData = [
//     { date: '2024-10-01', pnl: 300.13 },
//     { date: '2024-10-03', pnl: -280 },
//     { date: '2024-10-05', pnl: 600.20 },
//     { date: '2024-10-06', pnl: -157.24 },
//     { date: '2024-10-10', pnl: -100 },
//     { date: '2024-10-12', pnl: 28.30 },
//     { date: '2024-10-15', pnl: 53 },
//     { date: '2024-10-17', pnl: -10.9 },
//     { date: '2024-10-19', pnl: 215 },
//     { date: '2024-10-21', pnl: 433 },
// ];


let cumulativePnL = 0;
const chartData = window.TradeData.map(trade => {
    cumulativePnL += trade.pnl;
    return{
        date: trade.date,
        cumulativePnL: cumulativePnL
    }
})

const dates = chartData.map(item => item.date)
const pnlValues = chartData.map(item => item.cumulativePnL)

const lineChart = document.querySelector(".canvas-line-chart");

new Chart(lineChart, {
    type: "line",
    data: {
        labels: dates,
        datasets: [{
            label: "Cumulative PnL",
            data: pnlValues,
            borderColor: "green",
            backgroundColor: 'rgba(0, 255, 0, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.1
        }]
    },
    options:{
        responsive: true,
        maintainAspectRatio: false,
        scales:{
            x: {
                title: {
                    display: true,
                    text: "trade date"
                },
                ticks: {
                    autoSkip: true,
                    maxTicksLimit: 10
                }
            },
            y: {
                title: {
                    display: true,
                    text: "Cumulative PnL"
                },
                beginAtZero: false
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks:{
                    label: function(context){
                        return `PnL: $${context.raw.toFixed(2)}`
                    }
                }
            }
        }
    }
})


document.getElementById('apply-filter').addEventListener('click', function() {
    // Get filter values
    const filterWin = document.getElementById('filter_win').checked;
    const filterLoss = document.getElementById('filter_loss').checked;
    const minProfit = parseFloat(document.getElementById('min_profit').value) || -Infinity;
    const maxProfit = parseFloat(document.getElementById('max_profit').value) || Infinity;
    const startDate = new Date(document.getElementById('start_date').value);
    const endDate = new Date(document.getElementById('end_date').value);
    const searchQuery = document.getElementById('search_pair').value.toLowerCase();

    // Get all rows in the table
    const rows = document.querySelectorAll('#trade-table tr'); // Adjusted to select all rows

    rows.forEach(row => {
        // Skip the header row
        if (row.querySelector('th')) return;

        const profitCell = row.cells[8];  // Profit/Loss column
        const profitValue = parseFloat(profitCell.textContent.trim());
        
        const dateCell = row.cells[1];  // Date column
        const tradeDate = new Date(dateCell.textContent.trim());
        
        const instrumentCell = row.cells[0];  // Instrument column
        const instrument = instrumentCell.textContent.toLowerCase();

        let showRow = true;

        // Win/Loss filters
        if (filterWin && profitValue <= 0) {
            showRow = false;
        }
        if (filterLoss && profitValue >= 0) {
            showRow = false;
        }

        // Profit range filter
        if (profitValue < minProfit || profitValue > maxProfit) {
            showRow = false;
        }

        // Date range filter
        if (startDate && tradeDate < startDate) {
            showRow = false;
        }
        if (endDate && tradeDate > endDate) {
            showRow = false;
        }

        // Instrument search filter
        if (searchQuery && !instrument.includes(searchQuery)) {
            showRow = false;
        }

        row.style.display = showRow ? '' : 'none';
    });
});

// Real-time search for instrument
document.getElementById('search_pair').addEventListener('input', function() {
    const searchQuery = this.value.toLowerCase();

    const rows = document.querySelectorAll('#trade-table tr');

    rows.forEach(row => {
        // Skip the header row
        if (row.querySelector('th')) return;

        const instrumentCell = row.cells[0];  // Instrument column
        const instrument = instrumentCell.textContent.toLowerCase();

        row.style.display = instrument.includes(searchQuery) ? '' : 'none';
    });
});
