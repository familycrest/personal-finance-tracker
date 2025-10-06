/* static/js/make-it-rain.js */
console.log("Dollar rain JS loaded");

/* add this so the js waits until the page loads */
window.addEventListener('DOMContentLoaded', () => {
    const dollarRainContainer = document.getElementById("make-it-rain");

    function createDollar() {
        const dollar = document.createElement("div");
        dollar.classList.add("dollar");
        dollar.textContent = "$";

        // Make it start at a random horizontal position
        dollar.style.left = Math.random() * window.innerWidth + "px";

        // Have the dollar signs be a random size
        const size = Math.random() * 24 + 12; // 12px to 36px
        dollar.style.fontSize = size + "px";

        // Make the speed the dollar signs fall random
        const duration = Math.random() * 3 + 2; // 2s to 5s
        dollar.style.animationDuration = duration + "s";

        dollarRainContainer.appendChild(dollar);

        // Remove dollar signs after they fall and exit screen view
        setTimeout(() => {
            dollar.remove();
        }, duration * 1000);
    }

    // Create new dollar signs every 100ms to keep the vibes going
    setInterval(createDollar, 100);
});

