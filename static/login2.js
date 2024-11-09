let wrapper = document.querySelector(".wrapper");
let signUpLink = document.querySelector(".signup-link");
let loginLink = document.querySelector(".login-link")

signUpLink.addEventListener("click", () => {
    wrapper.classList.add("active");
});


loginLink.addEventListener("click", () => {
    wrapper.classList.remove("active");
});


let currentStep = 1;

function showStep(step) {
    document.getElementById(`step-1`).style.display = step === 1 ? 'block' : 'none';
    document.getElementById(`step-2`).style.display = step === 2 ? 'block' : 'none';
}

function nextStep() {
    currentStep = 2;
    showStep(currentStep);
}

function previousStep() {
    currentStep = 1;
    showStep(currentStep);
}

// Initialize the form to show the first step
showStep(currentStep);