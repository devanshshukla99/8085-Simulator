document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("assemble".onclick = () => {
        const request = new XMLHttpRequest();
        request.open("POST", `/assemble`);
        request.onload = () => {
            const response = request.responseText;
            console.load(response)
            document.getElementById("memory-container").innerHTML = response;
        }
    })
});