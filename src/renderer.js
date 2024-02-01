document.addEventListener("DOMContentLoaded", () => {
    const askButton = document.getElementById("askButton")
    const text = document.getElementById("text")
    let count = 0
        const askButtonClicked = async () => {
            count += 1
            text.textContent = "Ask Button clicked " + (count).toString()+" times"
        }
        askButton.addEventListener("click", askButtonClicked)
});