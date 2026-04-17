let zonesData = [];
let currentZone = 0;

async function loadLocationData() {
    const res = await fetch("/location-data");
    const data = await res.json();

    zonesData = data.zones;

    document.getElementById("zones").innerText = data.total_zones;
    document.getElementById("attendees").innerText = data.total_attendees;
    document.getElementById("cameras").innerText = data.active_cameras;
    document.getElementById("capacity").innerText = data.avg_capacity + "%";

    document.getElementById("zoneA").innerText = zonesData[0].people;
    document.getElementById("zoneB").innerText = zonesData[1].people;

    updateZoneDetails(currentZone);
}

function selectZone(index) {
    currentZone = index;
    updateZoneDetails(index);
}

function updateZoneDetails(index) {
    const zone = zonesData[index];

    document.getElementById("zoneTitle").innerText = zone.name;
    document.getElementById("zoneStatus").innerText = zone.status;

    // Dynamic status color
    const statusEl = document.getElementById("zoneStatus");
    statusEl.className = "status " + zone.status.toLowerCase();

    document.getElementById("zoneName").innerText =
        index === 0 ? "North Area" : "South Area";

    document.getElementById("zoneDesc").innerText =
        index === 0 ? "High traffic entry zone" : "Secondary area with light traffic";

    document.getElementById("cameraCount").innerText =
        "📷 " + (index + 1);

    document.getElementById("temperature").innerText =
        "🌡️ " + (22 + index) + "°C";

    // Progress bar
    const percent = (zone.people / zone.capacity) * 100;
    document.getElementById("progressFill").style.width = percent + "%";
}

// Auto refresh
setInterval(loadLocationData, 2000);
loadLocationData();