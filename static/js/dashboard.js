let peopleHistory = [];
let timeLabels = [];

const ctx = document.getElementById("countChart").getContext("2d");

const chart = new Chart(ctx, {
    type: "line",
    data: {
        labels: timeLabels,
        datasets: [{
            label: "People Count",
            data: peopleHistory,
            borderColor: "#3b82f6",
            backgroundColor: "rgba(59,130,246,0.2)",
            fill: true,
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: { beginAtZero: true }
        }
    }
});

// ================= HEATMAP REFRESH =================
function refreshHeatmap() {
    const img = document.getElementById("heatmapImage");
    if (!img) return;
    img.src = "/heatmap_feed?t=" + new Date().getTime();
}

setInterval(refreshHeatmap, 1000);
refreshHeatmap();

// ================= DASHBOARD DATA =================
setInterval(() => {
    fetch("/report-data")   // ✅ FIXED ENDPOINT
        .then(res => res.json())
        .then(data => {
            console.log("Dashboard Data:", data);

            const totalPeople = data.total_unique_people ?? 0;
            const aggression = data.aggression_incidents ?? 0;
            const density = data.peak_crowd_density ?? 0;

            document.getElementById("totalPeople").innerText = totalPeople;
            document.getElementById("aggressionCount").innerText = aggression;
            document.getElementById("density").innerText = density + "%";

            const now = new Date().toLocaleTimeString();
            timeLabels.push(now);
            peopleHistory.push(totalPeople);

            if (timeLabels.length > 10) {
                timeLabels.shift();
                peopleHistory.shift();
            }
            chart.update();

            if (aggression > 0) {
                const alert = document.createElement("li");
                alert.textContent = "Aggression detected at " + now;
                document.getElementById("alertList").prepend(alert);

                const timeline = document.createElement("li");
                timeline.textContent = now + " - Aggressive behavior detected";
                document.getElementById("timeline").prepend(timeline);
            }
        })
        .catch(err => console.error("Dashboard fetch error:", err));
}, 2000);
