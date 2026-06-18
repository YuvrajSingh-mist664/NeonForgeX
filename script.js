fetch("/save_score", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        player: "Yuvraj",
        score: score
    })
});