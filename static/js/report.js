function loadReportData() {
    const start = document.getElementById("startDate")?.value;
    const end = document.getElementById("endDate")?.value;

    let url = "/report-data";
    if (start && end) {
        url += `?start=${start}&end=${end}`;
    }

    fetch(url)
        .then(res => res.json())
        .then(data => {

            document.getElementById("totalAttendees").innerText =
                data.total_unique_people ?? 0;

            document.getElementById("aggressionIncident").innerText =
                data.aggression_incidents ?? 0;

            document.getElementById("peakDensity").innerText =
                (data.peak_crowd_density ?? 0) + "%";

            // 🔥 FIX: Always show chart
            const values = data.incidents_over_time && data.incidents_over_time.length
                ? data.incidents_over_time
                : [0, 0, 0, 0, 0];

            drawIncidentChart(values);
        })
        .catch(err => console.error("Report fetch error:", err));
}

let reportChart = null;

function drawIncidentChart(values) {
    const ctx = document.getElementById("incidentChart").getContext("2d");

    if (reportChart) reportChart.destroy();

    reportChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: values.map((_, i) => `T${i + 1}`),
            datasets: [{
                label: "Aggression Incidents",
                data: values,
                borderColor: "#ef4444",
                backgroundColor: "rgba(239,68,68,0.2)",
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function generateReport() {
    window.open("/generate-report", "_blank");
}

function exportPDF() {
    window.open("/generate-report", "_blank");
}

document.addEventListener("DOMContentLoaded", loadReportData);