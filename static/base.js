document.addEventListener("DOMContentLoaded", function(){
    const currentPageUrl = window.location.pathname;


    const pagesMapping = {
        "forex.html": "dashboard",
        "journal": "journalss",
        "All-trades": "all_trades",
        "playBook": "Play_book",
        "reports": "reports",
        "rules": "rules"
    }

    const pageName = currentPageUrl.split("/").pop();

    const activeId = pagesMapping[pageName]

    document.querySelectorAll("ul li a").forEach(link => {
        link.classList.remove("active")
    })

    if (activeId){
        const activeElement = document.getElementById(activeId);
        if (activeElement) {
            activeElement.classList.add("active");
        }
    }

})