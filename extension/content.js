let lastTitle = "";
function sendTitle() {
    let title = document.title;
    if (title === "YouTube" || title === "") return;
    if (title !== lastTitle) {
        lastTitle = title;
        console.log("Sending:", title);
        
        // Change localhost in URL to your IPv4 address here and in manifest.json
        fetch("http://localhost:5000/title", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ title: title })
        }).catch(err => console.error("Could not connect to Python server:", err));
    }
}
sendTitle();
setInterval(sendTitle, 2000);