

const ctx = document.getElementById("lineChart").getContext("2d");
const dough = document.getElementById("winRate-doughnut").getContext("2d")
const distribution = document.getElementById("trade-distribution").getContext("2d")
const performanceChart = document.getElementById("trade-performance").getContext("2d")

const customCenterTextPlugin = {
    id: "customCenterText",
    beforeDraw(chart) {
      const { width, height, ctx } = chart; // Use the correct context from the chart object
      ctx.save();
  
      // Calculate the center of the chart
      const centerX = width / 2;
      const centerY = height / 2;
  
      // Add the main percentage text
      ctx.font = "35px 'Poppins', sans-serif";
      ctx.fillStyle = "#000"; // Black text color
      ctx.textAlign = "center";
      ctx.textBaseline = "middle"; // Aligns text vertically
      ctx.fillText(`${window.winRate}%`, centerX, centerY - 20);
  
      // Add the secondary label text
      ctx.font = "15px 'Roboto', sans-serif";
      ctx.fillStyle = "#666"; // Gray text color
      ctx.fillText("Win Rate", centerX, centerY + 20);
  
      ctx.restore();
    },
  };
  
  // Register the custom plugin
//   Chart.register(customCenterTextPlugin);
  





const data = {
    labels: ["Jan", "Feb", "Mar", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    datasets: [
        {
            label: "GBPUSD",
            data: [200, 300, 150, 500, 450, 78, 250, 310, 370, 350, 420, 500],
            borderColor: "#182739",
            backgroundColor: "#182739",
            tension: 0.4,
            fill: false,
        },
        {
            label: "GBPJPY",
            data: [80, 90, 150, 120, 200, 250, 300, 310, 390, 376, 400, 420],
            borderColor: "#336496c9",
            backgroundColor: "#336496c9",
            tension: 0.4,
            fill: false
        },
        {
            label: "XAUUSD",
            data: [100, 90, 140, 230, 400, 350, 510, 490, 534, 568, 543, 579],
            borderColor: "#9dbedc",
            backgroundColor: "#9dbedc",
            tension: 0.4,
            fill: false
        },
    ]
};

const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        tooltip: {
            callbacks: {
                title: (tooltipItems) => {
                    return tooltipItems[0].label
                },
                label: (tooltipItem) => {
                    return `${tooltipItem.dataset.label}: ${tooltipItem.raw} hrs`;
                }
            }
        },
        legend: {
            display: true,
            position: "top",
            labels: {
                usePointStyle: true,
                pointStyle: "rectRounded",
                font: {
                    size: 14,
                    weight: "bold"
                },
                color: "#333",
                boxWidth: 15,
                boxHeight: 15,
                padding: 10,
            },
            align: "center"
        }
    },
    scales:{
        y: {
            beginAtZero: true
        }
    }
};


const doughData = {
    labels: ["Consumed", "Untapped"],
    datasets: [{
        data: [window.winRate, 100 - window.winRate],
        backgroundColor: ['#182739', '#cbdcec'],
        borderWidth: 0,
        hoverOffset: 4,
        borderRadius: (ctx) => {
            if (ctx.dataIndex === 0) {
                return 30;  // Set border radius for the consumed slice (30 for a more circular feel)
            }
            return 0; 
        }
    }]
};


const doughOptions = {
    plugins: {
        legend: {
            display: true,
            position: "bottom",
            labels: {
                userPointStyle: true,
                boxWidth: 10,
            }
        },
    },
    // cutoutPercentage: 90,
    cutout: "90%",
    responsive: true,
    maintainAspectRatio: false,
    
}

const distributionData = {
    labels:["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    datasets: [{
        label: "trades",
        data: window.distribution,
        backgroundColor: "#2a517a",
        borderWidth: 1,
    }]
}

const distributionOptions = {
    indexAxis: "y",
    responsive: true,
    plugins: {
        legend: {
            display: false,
            // position: "top"
        },
        tooltip: {
            enabled: true
        }
    },
    scales: {
        x: {
            beginAtZero: true,
        },
        y: {
            ticks: {
                autoSkip: false,
            }
        }
    }
}

const performanceData = {
    labels: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    datasets: [{
        label: "PnL",
        data: window.profit,
        backgroundColor: "#9dbedc",
        borderWidth: 1,
    }]
}

const performanceOptions = {
    indexAxis: "y",
    responsive: true,
    plugins: {
        legend: {
            display: false
        },
        tooltip: {
            enabled: true
        }
    },
    scales: {
        x: {
            beginAtZero: true
        },
        y: {
            ticks: {
                autoSkip: false
            }
        }
    }
}


new Chart(performanceChart, {
    type: "bar",
    data: performanceData,
    options: performanceOptions
})


new Chart(distribution, {
    type: "bar",
    data: distributionData,
    options: distributionOptions
})


new Chart(dough, {
    type: "doughnut",
    data: doughData,
    options: doughOptions,
    plugins: [customCenterTextPlugin],
})




new Chart(ctx, {
    type: "line",
    data: data,
    options: options
})



