// document.querySelectorAll(".trade-card").forEach(card => {
//     card.addEventListener("click", (event) => {
//         const tradeId = card.dataset.tradeId
//         const tradeticket = card.getAttribute("data-trade-id");
//         const tradeProfit = card.getAttribute("data-trade-profit");
//         const tradeSymbol = card.getAttribute("data-trade-symbol");
//         console.log(tradeId)
//         document.getElementById("rich-text-container").style.display = "block";
//         document.getElementById("save-journal").style.display = "block";
//         displayTradeDetails(tradeId, tradeProfit, tradeSymbol);
//         initializeEditor(tradeId)
//     })
// })

// function initializeEditor(tradeId){
//     console.log("I'm quill")
//     const quill = new Quill('#journal-text', {
//         theme: 'snow',
//         placeholder: 'Write your journal entry here...',
//         modules: {
//             toolbar: [
//                 [{ header: [1, 2, false] }],
//                 ['bold', 'italic', 'underline'],
//                 [{ list: 'ordered' }, { list: 'bullet' }],
//                 ['link', 'image'],
//                 ['clean']
//             ]
//         }
//     });

//     document.getElementById('save-journal').addEventListener('click', () => {
//         const journalContent = quill.root.innerHTML;
//         saveJournalEntry(tradeId, journalContent);
//     });
// }

// function saveJournalEntry(tradeId, journalContent) {
//     fetch(`/save-journal/`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//         'X-CSRFToken': '{{ csrf_token }}'
//       },
//       body: JSON.stringify({
//         trade_id: tradeId,
//         journal_content: journalContent
//       })
//     })
//     .then(response => response.json())
//     .then(data => {
//       alert('Journal saved!');
//       // Optionally update the UI with the journal content
//       // For example, showing the journal preview next to the trade card
//       document.querySelector(`.trade-card[data-trade-id="${tradeId}"] .journal-preview`).textContent = journalContent;
//     })
//     .catch(error => console.error('Error saving journal:', error));
//   }

//   function displayTradeDetails(id, profit, symbol) {
//     // Find the element where you want to display the trade details
//     document.getElementById("ticket").textContent = `Ticket: ${id}`
//     document.getElementById("symbol").textContent = `Ticket: ${symbol}`
//     document.getElementById("profit").textContent = `Ticket: ${profit}`

    
// }

// // const quill = new Quill('#journal-text', {
// //     theme: 'snow',
// //     placeholder: 'Write your journal entry here...',
// //     modules: {
// //         toolbar: [
// //             [{ header: [1, 2, false] }],
// //             ['bold', 'italic', 'underline'],
// //             [{ list: 'ordered' }, { list: 'bullet' }],
// //             ['link', 'image'],
// //             ['clean']
// //         ]
// //     }
// // });

// Initialize Quill once
let quill;

function initializeEditor() {
    if (!quill) { // Initialize only if it hasn't been initialized
        console.log("here")
        quill = new Quill('#journal-text', {
            theme: 'snow',
            placeholder: 'Write your journal entry here...',
            modules: {
                toolbar: [
                    [{ header: [1, 2, false] }],
                    ['bold', 'italic', 'underline'],
                    [{ list: 'ordered' }, { list: 'bullet' }],
                    ['link', 'image'],
                    ['clean']
                ]
            }
        });

        // Add save functionality
        document.getElementById('save-journal').addEventListener('click', () => {
            const journalContent = quill.root.innerHTML;
            const tradeId = document.getElementById("ticket").dataset.tradeId; // Use data attribute for trade ID
            saveJournalEntry(tradeId, journalContent);
        });
    }
}

// Function to display trade details in the editor
function displayTradeDetails(tradeId, tradeProfit, tradeSymbol) {
    // Set trade details in the editor header
    const formattedProfit = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(tradeProfit);


    document.getElementById("rich-text-container").style.display = "block";
    document.getElementById("save-journal").style.display = "block";
    document.getElementById("ticket").textContent = `Ticket: ${tradeId}`;
    document.getElementById("symbol").textContent = `Symbol: ${tradeSymbol}`;
    document.getElementById("profit").textContent = `Profit: ${formattedProfit}`;
    document.getElementById("ticket").dataset.tradeId = tradeId; // Store trade ID in a data attribute


    fetch(`get-journal-note/${tradeId}`)
        .then(response => response.json())
        .then(data => {
            if (data.journal_content) {
                // Display existing journal entry
                quill.root.innerHTML = data.journal_content;
            } else {
                // No journal entry exists; clear the editor
                quill.root.innerHTML = '';
            }
        })
        .catch(error => console.error('Error fetching journal entry:', error));
    // Optional: Clear the editor content when a new trade is selected
    quill.root.innerHTML = '';
}
function getCSRFToken() {
    // Get CSRF token from the page
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
// Save journal entry function
function saveJournalEntry(tradeId, journalContent) {
    console.log(journalContent)
    fetch(`save-journal`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            trade_id: tradeId,
            journal_content: journalContent
        })
    })
    .then(response => response.json())
    .then(data => {
        alert('Journal saved!');
        // Optionally update the UI with a saved confirmation
    })
    .catch(error => console.error('Error saving journal:', error));
}
let lastClickedCard = null; 
// Event listener for each trade card
document.querySelectorAll(".trade-card").forEach(card => {
    card.addEventListener("click", (event) => {
        const tradeId = card.getAttribute("data-trade-id");
        const tradeProfit = card.getAttribute("data-trade-profit");
        const tradeSymbol = card.getAttribute("data-trade-symbol");
        if (lastClickedCard !== null) {
            lastClickedCard.style.backgroundColor = "";  // Reset to the normal color
        }

        // Highlight the clicked card
        card.style.backgroundColor = "lightblue";  // Or any color you'd like for the highlight

        // Update the last clicked card to the current one
        lastClickedCard = card;
        initializeEditor(); // Initialize the editor only once
        // Display trade details and initialize the editor if needed
        displayTradeDetails(tradeId, tradeProfit, tradeSymbol);
        
    });
});
