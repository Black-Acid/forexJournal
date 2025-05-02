const strategyButton = document.getElementById("modalsss")
const content = document.querySelector(".strategy-modal")
const closeModal = document.querySelector(".close-modal")
const overlay = document.querySelector(".play-overlay")


strategyButton.addEventListener("click", function(){
    content.classList.remove("hidden")
    overlay.classList.remove("hidden")
})

overlay.addEventListener("click", () => {
    content.classList.add("hidden")
    overlay.classList.add("hidden")
})






const nextButton = document.querySelector(".btn-next")
const prevButton = document.querySelector(".btn-prev")
const steps = document.querySelectorAll(".step")
const form_steps = document.querySelectorAll(".form-step")
let active = 1;



const updateProgress = () => {
    console.log('steps.length =>' + steps.length)
    console.log('active =>' + active)

    steps.forEach((step, i) => {
        if ( i == (active-1)){
            step.classList.add("active")
            form_steps[i].classList.add("active")
            console.log("i =>" + i)
        } else{
            step.classList.remove("active")
            form_steps[i].classList.remove("active")
        }
    })

    if (active === 1){
        prevButton.disabled = true
    } else if (active === steps.length){
        nextButton.disabled = true
    } else{
        prevButton.disabled = false
        nextButton.disabled = false
    }

}

console.log(nextButton)

nextButton.addEventListener("click", () => {
    console.log("I have been clicked")
    active++
    if (active > steps.length){
        active = steps.length;
    }
    updateProgress();
})

prevButton.addEventListener("click", () => {
    active--;
    if(active < 1){
        active = 1;
    }
    updateProgress();
})


document.addEventListener("DOMContentLoaded", function(){
    const strategyRows = document.querySelectorAll(".strategy-row");


    strategyRows.forEach(function(row){
        row.addEventListener("click", function(){
            const strategyId = Number(row.getAttribute("data-strategy-id"))
            window.location.href = `strategy-reports/${strategyId}`
        })
    })
})