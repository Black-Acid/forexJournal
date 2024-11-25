const ctx = document.getElementById("lineChart").getContext("2d");


const data = {
    labels: ["Jan", "Feb", "Mar", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    datasets: [
        {
            label: "GBPUSD",
            data: [200, 300, 150, 500, 450, 78, 250, 310, 370, 350, 420, 500],
            borderColor: "blue",
            tension: 0.4,
            fill: false,
        },
        {
            label: "GBPJPY",
            data: [80, 90, 150, 120, 200, 250, 300, 310, 390, 376, 400, 420],
            borderColor: "Cyan",
            tension: 0.4,
            fill: false
        },
        {
            label: "XAUUSD",
            data: [100, 90, 140, 230, 400, 350, 510, 490, 534, 568, 543, 579],
            borderColor: "yellow",
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
            position: "top"
        }
    },
    scales:{
        y: {
            beginAtZero: true
        }
    }
};

new Chart(ctx, {
    type: "line",
    data: data,
    options: options
})