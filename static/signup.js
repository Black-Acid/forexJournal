
const nextButton = document.querySelector(".next-btn")
const prevButton = document.querySelector(".previous-btn")
const steps = document.querySelectorAll(".step-form")
const form_steps = document.querySelectorAll(".forms-step")
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
        nextButton.disabled = false
    } else if (active === steps.length){
        nextButton.disabled = true
        prevButton.disabled = false
    } //else{
    //    prevButton.disabled = false
    //    nextButton.disabled = false
    //}

}

nextButton.addEventListener("click", () => {
    active++
    console.log("When the next button is clicked active = "+ active)
    console.log("When the next button is steps.length = "+ steps.length)
    if (active > steps.length){
        active = steps.length;
    }
    updateProgress();
})

prevButton.addEventListener("click", () => {
    active--;
    console.log(active)
    if(active < 1){
        active = 1;
    }
    updateProgress();
})