document.addEventListener('DOMContentLoaded', function() {  
    fetch("get-data")
        .then(response => response.json())
        .then(data => {
            console.log(data);  // Verify the fetched data

            // Aggregate profits by date
            const profitByDate = {};
            const tradeCountByDate = {}; // New object to count trades

            data.forEach(trade => {
                const profit = parseFloat(trade.profit_usd); // Extract profit as a number
                const date = trade.opening_time.split('T')[0]; // Get the date part

                // Aggregate profit
                if (!profitByDate[date]) {
                    profitByDate[date] = 0; // Initialize if not present
                }
                profitByDate[date] += profit; // Sum the profit for that date

                // Count trades
                if (!tradeCountByDate[date]) {
                    tradeCountByDate[date] = 0; // Initialize if not present
                }
                tradeCountByDate[date] += 1; // Increment trade count
            });
            var calendarEl = document.getElementById('calendar');
            var calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                height: window.innerHeight * 0.95,
                datesSet: function() {
                     // Select all day cells
                     var dayCells = document.querySelectorAll('.fc-daygrid-day');
                     dayCells.forEach(function(cell) {
                         const date = cell.getAttribute('data-date'); // Get the date from the cell
                         const totalProfit = profitByDate[date]; // Get the profit for that date
                         const tradeCount = tradeCountByDate[date] || 0; // Get the trade count for that date

                         const formatter = new Intl.NumberFormat('en-US', {
                            style: 'currency',
                            currency: 'USD',
                          });

                         cell.innerHTML = '';
                         if (totalProfit) {
                            cell.style.backgroundColor = totalProfit > 0 ? '#2ecc71' : '#ff6b6b'; // Set background color
                            cell.style.color = '#ffffff'; // Change text color for contrast

                            // Create a span for the profit text
                            const profitSpan = document.createElement('span');
                            profitSpan.textContent = `${formatter.format(totalProfit)}`;
                            profitSpan.style.position = 'absolute';
                            profitSpan.style.right = '5px'; 
                            profitSpan.style.bottom = '30px'; // Position it 5px from the bottom
                            profitSpan.style.textAlign = 'right'; // Align text to the right
                            profitSpan.style.fontSize = '30px'

                            cell.style.position = 'relative'; // Set position to enable absolute positioning
                            // cell.appendChild(profitSpan); 

                            const tradeSpan = document.createElement('span');
                            tradeSpan.textContent = `Trades: ${tradeCount}`;
                            tradeSpan.style.position = 'absolute';
                            tradeSpan.style.right = '5px'; 
                            tradeSpan.style.bottom = '5px'; // Position it closer to the bottom
                            tradeSpan.style.textAlign = 'right'; // Align text to the right
                            tradeSpan.style.fontSize = '16px'; // Smaller font size for trades

                            cell.style.position = 'relative'; // Set position to enable absolute positioning
                            cell.appendChild(profitSpan); // Append the profit span to the cell
                            cell.appendChild(tradeSpan);



                            cell.addEventListener("click", function(){
                                document.getElementById("trades-modal").classList.remove("hidden");
                                document.getElementById("overlay").classList.remove("hidden")
                            })

                         }
                     });
                },
                dateClick: function(info){
                    const clickedDate = new Date(info.date);
                    const day = clickedDate.toLocaleDateString("en-Us", {weekday: "short"})
                    const formattedDate = clickedDate.toISOString().split("T")[0]

                    console.log(`clicked date: ${clickedDate.toISOString().split("T")[0]}`)
                    console.log(`day of the week ${day}`)

                    document.getElementById("modal-date").textContent = `${day}, ${formatDate(clickedDate)}`

                    //filtering the tradesData that matches the formatted data
                    const tradesOnClickedDate = data.filter(trade =>{
                        const tradeDate = trade.opening_time.split("T")[0];
                        return tradeDate === formattedDate
                    })



                    const tablebody = document.getElementById("table-body");
                    tablebody.innerHTML = '';
                    if (tradesOnClickedDate.length > 0){
                        document.getElementById("total-trades").textContent = tradesOnClickedDate.length;
                        console.log(tradesOnClickedDate)
                        let count = 0;
                        let profit = 0;
                        let commision = 0;
                        let selectedTradeId = null
                        tradesOnClickedDate.forEach(trade => {
                            const tradeRow = document.createElement("tr");

                            tradeRow.setAttribute("data-trade-id", trade.ticket)

                            const instrument = document.createElement("td")
                            instrument.textContent = trade.symbol;

                            const open_time = document.createElement("td")
                            open_time.textContent = trade.opening_time.split("T")[0];

                            const position = document.createElement("td")
                            position.textContent = trade.order_type;

                            const PnL = document.createElement("td")
                            PnL.textContent = `$${parseFloat(trade.profit_usd).toFixed(2)}`;

                            const netROI = document.createElement("td")
                            netROI.textContent = "-";

                            const rrMultiple = document.createElement("td")
                            rrMultiple.textContent = "-";

                            const strategy = document.createElement("td")
                            strategy.textContent = "-";

                            
                            profit += Number(parseFloat(trade.profit_usd).toFixed(2))
                        
                            commision += Number(trade.commision_usd)

                            if (trade.profit_usd > 0){
                                count++;
                            }
                            tradeRow.appendChild(instrument)
                            tradeRow.appendChild(open_time)
                            tradeRow.appendChild(position)
                            tradeRow.appendChild(PnL)
                            tradeRow.appendChild(netROI)
                            tradeRow.appendChild(rrMultiple)
                            tradeRow.appendChild(strategy)

                            tablebody.appendChild(tradeRow)

                            tradeRow.addEventListener("click", function() {
                                // Remove highlight from previously selected row (if any)
                                const previouslySelected = document.querySelector("tr.selected");
                                if (previouslySelected) {
                                    previouslySelected.classList.remove("selected");
                                }
                        
                                // Add highlight to the clicked row
                                this.classList.add("selected");
                        
                                // Store the trade_id of the selected row
                                selectedTradeId = this.getAttribute("data-trade-id");
                                
                            });

                            

                        });

                        const viewDetailsButton = document.getElementById("view-details-button");
                            viewDetailsButton.addEventListener("click", function() {
                                if (selectedTradeId) {
                                    // Redirect to the journal page with the selected trade_id
                                    window.location.href = `journal/${selectedTradeId}`;
                                } else {
                                    alert("Please select a trade to view details.");
                            }
                        });

                        document.getElementById("winners").textContent = count
                        document.getElementById("pnl").textContent = profit.toFixed(2)
                        document.getElementById("Net-Pnl").textContent = profit.toFixed(2)
                        
                    }

                    // tablebody.addEventListener("click", function(event) {
                    //     const clickedRow = event.target.closest("tr");
                    //     if (clickedRow) {
                    //         let tradeId = clickedRow.getAttribute("data-trade-id");
                    //         console.log(tradeId);
                    //         window.location.href = `journal/${tradeId}`;
                    //     }
                    // });

                    // sending the date clicked with it's day to my dajngo views

                    fetch("All-trades",{
                        method: "POST",
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            date: clickedDate.toISOString().split("T")[0],
                            day: day
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log(`response from server ${data}`);
                        // window.location.href = "All-trades"
                    })
                    .catch(error => console.error(`Error: ${error}`))


                }
             });
            calendar.render();
            const close = document.querySelector(".close-modal");
            close.addEventListener("click", function(){
                document.getElementById("trades-modal").classList.add("hidden")
                document.getElementById("overlay").classList.add("hidden")
            })
        })
        .catch(error => console.log("Error fetching data: ", error));  // Correctly chained .catch
})


function getCookie(name){
    let cookieValue = null;
    if (document.cookie && document.cookie !== ''){
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++){
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")){
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue
}


function formatDate(dateString){
    const options = {
        year: "numeric",
        month: "short",
        day: "numeric"
    };
    return new Intl.DateTimeFormat("en-US", options).format(dateString)
}