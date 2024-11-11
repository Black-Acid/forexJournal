document.querySelectorAll(".trade-card").forEach(card => {
    card.addEventListener("click", (event) => {
        const tradeId = card.dataset.tradeId
        console.log(tradeId)
        // document.getElementById("rich-text-container").style.display = "block";
        initializeEditor(tradeId)
    })
})

function initializeEditor(tradeId){
    console.log("I'm quill")
    const quill = new Quill('#journal-text', {
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

    document.getElementById('save-journal').addEventListener('click', () => {
        const journalContent = quill.root.innerHTML;
        saveJournalEntry(tradeId, journalContent);
    });
}

function saveJournalEntry(tradeId, journalContent){
    console.log(journalContent)
}

// const quill = new Quill('#journal-text', {
//     theme: 'snow',
//     placeholder: 'Write your journal entry here...',
//     modules: {
//         toolbar: [
//             [{ header: [1, 2, false] }],
//             ['bold', 'italic', 'underline'],
//             [{ list: 'ordered' }, { list: 'bullet' }],
//             ['link', 'image'],
//             ['clean']
//         ]
//     }
// });