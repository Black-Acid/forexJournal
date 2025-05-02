'use strict'

let healthyTrades = document.querySelector(".healthy").textContent
let healthyNumericContent = parseInt(healthyTrades)

let luckyTrades = document.querySelector(".lucky").textContent
let luckyNumericContent = parseInt(luckyTrades);

let goodLoss = document.querySelector(".good_loss").textContent;
let goodLossNumericContent = parseInt(goodLoss);

let badTrades = document.querySelector(".bad").textContent;
let badTradesNumericContent = parseInt(badTrades);

let missedTrades = document.querySelector(".missed").textContent;
let missedTradesNumericContent = parseInt(missedTrades);

let untaggedTrades = document.querySelector(".untagged").textContent;
let untaggedTradesNumericContent = parseInt(untaggedTrades);




const chartData = {
    labels: ["healthy Trades", "Lucky trades", "Good lost Trades", "Bad lost trades", "Missed trades", "Untagged Trades"],
    data: [healthyNumericContent, luckyNumericContent, goodLossNumericContent, badTradesNumericContent, missedTradesNumericContent, untaggedTradesNumericContent]
}

const centerTextPlugin = {
    id: 'centerText',
    beforeDraw: function(chart) {
        const {width, height, ctx} = chart;
        ctx.restore();

        // Set font properties for the first line (bold "12")
        let fontSize = (height / 100).toFixed(2);  // Adjust size as needed
        ctx.font = `bold ${fontSize}em Arial`;  // Bold font for "12"
        ctx.fillStyle = "#FFFFFF";  // White color
        ctx.textBaseline = "middle";
        ctx.textAlign = "center";

        // Draw the first line of text
        const text1 = "0";
        const textX = width / 2;
        const textY = height / 2 - 10;  // Adjust Y position to move it slightly up
        ctx.fillText(text1, textX, textY);

        // Set font properties for the second line (regular "solid trades")
        fontSize = (height / 200).toFixed(2);  // Smaller font size for "solid trades"
        ctx.font = `${fontSize}em Arial`;
        ctx.fillStyle = "#FFFFFF";  // White color

        // Draw the second line of text
        const text2 = "solid trades";
        const textY2 = height / 2 + 20;  // Adjust Y position to place it under "12"
        ctx.fillText(text2, textX, textY2);

        ctx.save();
    }
};

// Chart.register(centerTextPlugin);

if (window.totalTrades != 0){
    const myChart = document.querySelector(".my-chart");

    new Chart(myChart, {
        type: "doughnut",
        data: {
            labels: chartData.labels ,
            datasets: [
                {
                    label: "Trades",
                    data: chartData.data,
                    backgroundColor: [
                        "#243b55", 
                        "#264666", 
                        "#2a517a", 
                        "#336496",
                        "#447eb3", 
                        "#689bc8",
                    ],
                    borderWidth: 0,
                }
            ]
        },
        options: {
            cutout: '65%', 
            plugins: {
                legend: {
                    display: false
                }
            }
        },
        plugins: [centerTextPlugin]  // Apply the custom plugin
    })

}

if (window.totalTrades != 0){
    const some = document.getElementById('lineChart').getContext('2d');
    const gradient = some.createLinearGradient(0, 0, 0, 400);  // Adjust the gradient dimensions as needed
    gradient.addColorStop(0, '#004d00');  // Dark green at the bottom
    gradient.addColorStop(1, '#00FF00');

    let cumulativePnL = 0;
    const NewchartData = window.trades.map(trade => {
        cumulativePnL += trade.pnl;
        return{
            date: trade.date,
            cumulativePnL: cumulativePnL
        }
    })

    const Newdates = NewchartData.map(item => item.date)
    const NewpnlValues = NewchartData.map(item => item.cumulativePnL)




    new Chart(some, {
        type: 'line',
        data: {
        labels: Newdates,
        datasets: [{
            label: 'Cumulative Profits',
            data: NewpnlValues,
            borderWidth: 1,
            tension: 0.4,
            borderColor: "#182739",
            fill: true,
            backgroundColor: '#689bc855',
            //pointRadius: 0,
        }]
        },
        options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            const label = tooltipItems[0].label;
                            return `Total Profits\n${label}, 2024`;  // Customize title
                        },
                        label: function(tooltipItem) {
                            const value = tooltipItem.raw;
                            return `$${value.toLocaleString()}`;  // Format value as currency
                        }
                    },
                    backgroundColor: '#000',  // Tooltip background color
                    titleColor: '#FFF',  // Title color
                    bodyColor: '#FFF',  // Body color
                    borderColor: '#FFF',  // Border color
                    borderWidth: 0.5,  // Border width
                    padding: 10  // Padding inside the tooltip
                },
                legend: {
                    display: false
                }
            },
        scales: {
            x: {
                ticks: {
                    display: false  // Hide x-axis labels
                },
                grid: {
                    display: true,  // Optionally hide x-axis grid lines
                    color: 'rgba(255, 255, 255, 0.5)',  // Set grid line color to white with 50% opacity
                    lineWidth: 0.2  // Set grid line width
                }
            },
            y: {
                ticks: {
                    display: false  // Hide y-axis labels
                },
                grid: {
                    display: true,  // Optionally hide y-axis grid lines
                    color: 'rgba(255, 255, 255, 0.5)',  // Set grid line color to white with 50% opacity
                    lineWidth: 0.2  // Set grid line width
                },
            beginAtZero: true
            }
        }
        }
    });
}




const showModal = document.querySelector(".show-modal")
const modal = document.querySelector(".modal")
const overlay = document.querySelector(".modal-overlay")
const closes = document.querySelector(".close-modal")

const Transfer = document.getElementById('Transfer');
const Transfer2 = document.getElementById("Transfer2")
    
const closeModal = function(){
    modal.classList.add("hidden")
    overlay.classList.add("hidden")
    Transfer.classList.add("hidden")
    Transfer2.classList.add("hidden")
}


showModal.addEventListener("click", function(){
    modal.classList.remove("hidden")
    overlay.classList.remove("hidden")
})

closes.addEventListener("click", closeModal)
overlay.addEventListener("click", closeModal)


// Toggle dropdown visibility
document.querySelector('.dropdown-button').addEventListener('click', function () {
    const dropdown = document.querySelector('.custom-dropdown');
    dropdown.classList.toggle('open');
  });
  
  // Handle item selection
  document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', function () {
      const value = this.getAttribute('data-value');
      const text = this.textContent.trim();
      
      // Update the input field with the selected item
      const input = document.querySelector('#broker');
      input.value = text;
  
      // Close the dropdown
      document.querySelector('.custom-dropdown').classList.remove('open');
    });
  });


// Get the button and menu elements
const dotsButton = document.querySelector('.vertical-dots');
const dropdownMenu = document.getElementById('dropdownMenu');
const deposit = document.getElementById('depositBtn');
const withdraw = document.getElementById('withdrawBtn');




// Add event listener to the dots button to toggle the menu
dotsButton.addEventListener('click', function() {
    // Toggle the display property to show/hide the menu
    dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
});

withdraw.addEventListener("click", function(){
    
    Transfer2.classList.remove("hidden")
    overlay.classList.remove("hidden")
})

deposit.addEventListener("click", function(){
    Transfer.classList.remove("hidden")
    overlay.classList.remove("hidden")

})

// Optional: Close the menu if the user clicks outside of it
document.addEventListener('click', function(event) {
    if (!dotsButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
        dropdownMenu.style.display = 'none';
    }
});

  
const fileInput = document.getElementById('broker');
const fileNameDisplay = document.getElementById('fileName');

console.log(fileNameDisplay.textContent)
fileInput.addEventListener('change', function () {
    console.log(fileNameDisplay.textContent)
    if (fileInput.files.length > 0) {
        fileNameDisplay.textContent = `Uploaded: ${fileInput.files[0].name}`;
        console.log(fileNameDisplay.textContent)
    } else {
        fileNameDisplay.textContent = ''; // Clear if no file
    }
});