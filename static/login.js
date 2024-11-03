// document.addEventListener("DOMContentLoaded", function() {
//     const typewriterElement = document.querySelector(".typewriter")
//     const text = typewriterElement.textContent
//     const typingSpeed = 100; // Typing speed in milliseconds
//     let i = 0;

//     typewriterElement.textContent = ""; 

//     function typeWriter() {
//         if (i < text.length) {
//             if (i === 11) {
//                 typewriterElement.style.color = "red"; // Change color directly
//             } else {
//                 typewriterElement.style.color = "black"; // Reset color to default
//             }
//             typewriterElement.textContent += text.charAt(i); // Add one character at a time
//             i++;
//             setTimeout(typeWriter, typingSpeed);
//         }
//     }

//     typeWriter();
    
    
// });



document.addEventListener("DOMContentLoaded", function() {
    const typewriterElement = document.querySelector(".typewriter");
    const text = typewriterElement.textContent;
    const typingSpeed = 100; // Typing speed in milliseconds
    let i = 0;

    // Clear the typewriter element's content
    typewriterElement.textContent = ""; 

    function typeWriter() {
        if (i < text.length) {
            // Create a text node for the current character
            const charNode = document.createTextNode(text.charAt(i));

            // If i is greater than 10, change the color to green
            if (i > 10) {
                const span = document.createElement("span");
                span.style.color = "rgb(3, 226, 3)"; // Set the text color to green
                span.appendChild(charNode); // Append the character to the span
                typewriterElement.appendChild(span); // Append the span to the typewriter element
            } else {
                typewriterElement.appendChild(charNode); // Append the character normally
            }

            i++;
            setTimeout(typeWriter, typingSpeed);
        }
    }

    typeWriter();
});
