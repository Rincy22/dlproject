async function loadSettings() {
    const res = await fetch("/get-settings");
    const data = await res.json();

    document.getElementById("name").value = data.name;
    document.getElementById("email").value = data.email;
    document.getElementById("phone").value = data.phone;
    document.getElementById("department").value = data.department;

    document.getElementById("email_alerts").checked = data.email_alerts;
    document.getElementById("sms_alerts").checked = data.sms_alerts;
    document.getElementById("push_notifications").checked = data.push_notifications;

    document.getElementById("profileName").innerText = data.name;
}

function showTab(tab) {
    document.getElementById("profileTab").style.display = tab === "profile" ? "block" : "none";
    document.getElementById("notificationTab").style.display = tab === "notification" ? "block" : "none";

    document.getElementById("profileBtn").classList.toggle("active", tab === "profile");
    document.getElementById("notifyBtn").classList.toggle("active", tab === "notification");
}

async function saveSettings() {
    const data = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value,
        department: document.getElementById("department").value,

        email_alerts: document.getElementById("email_alerts").checked,
        sms_alerts: document.getElementById("sms_alerts").checked,
        push_notifications: document.getElementById("push_notifications").checked
    };

    await fetch("/save-settings", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });

    alert("Settings Saved!");
}

loadSettings();