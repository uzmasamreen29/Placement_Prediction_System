// Complete upgraded static/script.js

document.addEventListener("DOMContentLoaded", function () {

    console.log("Student Placement Prediction System Loaded Successfully");

    const button = document.querySelector("button");

    if (button) {
        button.addEventListener("click", function () {
            button.innerText = "Predicting...";
            button.style.background = "#00ffcc";
        });
    }

    // Smooth scroll to result section after prediction
    const resultBox = document.querySelector(".result-box");

    if (resultBox) {
        resultBox.scrollIntoView({
            behavior: "smooth"
        });
    }

});