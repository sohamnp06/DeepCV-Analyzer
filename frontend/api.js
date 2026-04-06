// Centralized API client — used by login, signup, upload pages
function getBaseUrl() {
    return (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL)
           ? window.APP_CONFIG.API_BASE_URL
           : "http://127.0.0.1:8080";
}

async function apiCall(endpoint, options = {}) {
    const base = getBaseUrl();
    const url = base + endpoint;

    // Default headers
    if (!options.headers) options.headers = {};

    // Smart JSON handling: If body is a plain object, stringify it and set Content-Type
    if (options.body && !(options.body instanceof FormData) && typeof options.body === 'object') {
        options.body = JSON.stringify(options.body);
        options.headers['Content-Type'] = 'application/json';
    }

    try {
        const res = await fetch(url, options);
        if (!res.ok) {
            const body = await res.json().catch(() => ({ detail: "Server error" }));
            throw new Error(body.detail || "Request failed");
        }
        return await res.json();
    } catch (err) {
        if (err.message === "Failed to fetch") {
            throw new Error("Cannot reach backend at " + base + ". Please check your internet or if the server is awake.");
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
