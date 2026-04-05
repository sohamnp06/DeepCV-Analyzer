// Centralized API client — used by login, signup, upload pages
function getBaseUrl() {
    return (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL)
           ? window.APP_CONFIG.API_BASE_URL
           : "http://127.0.0.1:8080";
}

async function apiCall(endpoint, options) {
    const base = getBaseUrl();
    const url = base + endpoint;

    try {
        const res = await fetch(url, options);
        if (!res.ok) {
            const body = await res.json().catch(() => ({ detail: "Server error" }));
            throw new Error(body.detail || "Request failed");
        }
        return await res.json();
    } catch (err) {
        if (err.message === "Failed to fetch") {
            throw new Error("Cannot reach backend at " + base + ". Is it running?");
        }
        throw err;
    }
}

function requireAuth() {
    const uid = localStorage.getItem("user_id");
    if (!uid) { window.location.href = "login.html"; return null; }
    return uid;
}

function logout() {
    localStorage.removeItem("user_id");
    localStorage.removeItem("username");
    localStorage.removeItem("last_result");
    window.location.href = "login.html";
}
