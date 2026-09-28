import axios from "axios";

// ------------------------------------------------------------------
// ADDED: RUNTIME-CONFIGURABLE SERVER ADDRESS
// ------------------------------------------------------------------
// Before this change, the backend's address was either "" (relative
// URLs, only works if frontend + backend are same-origin behind a
// reverse proxy) or a Vite build-time env var - meaning changing the
// server's IP meant editing .env and running `npm run build` again.
//
// Now the app reads /server-config.json at startup - a plain JSON
// file that sits next to index.html in the deployed `dist` folder
// (see dashboard/public/server-config.json, which Vite copies as-is
// into dist/ on build). To point this dashboard at a new server IP,
// just edit that ONE file on the server PC and refresh the browser -
// no rebuild, no redeploy, no touching any .js file.
//
//   { "apiBaseUrl": "" }
//     -> same-origin / relative URLs (default - unchanged behaviour,
//        use this if you put a reverse proxy in front of both apps)
//
//   { "apiBaseUrl": "http://192.168.1.50:8000" }
//     -> talk to the backend directly at that address. Requires
//        ALLOWED_ORIGINS to be set on the backend (see backend/.env
//        and backend/app/main.py) so the browser's CORS check passes.
export let API_BASE_URL = "";

let configLoadPromise = null;

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Call this once, before the app renders (see src/main.jsx). Safe to
// call more than once - later calls just reuse the first result.
export function loadRuntimeConfig() {
  if (configLoadPromise) return configLoadPromise;

  configLoadPromise = fetch("/server-config.json", { cache: "no-store" })
    .then((res) => (res.ok ? res.json() : {}))
    .catch(() => ({}))
    .then((data) => {
      if (data && typeof data.apiBaseUrl === "string" && data.apiBaseUrl.trim()) {
        API_BASE_URL = data.apiBaseUrl.trim().replace(/\/+$/, "");
      }
      client.defaults.baseURL = API_BASE_URL;
      return API_BASE_URL;
    });

  return configLoadPromise;
}

// Derives the WebSocket origin from API_BASE_URL so useWebSocket.js
// talks to the same host the REST calls go to, instead of always
// assuming the API lives on the page's own origin (which breaks once
// apiBaseUrl points somewhere else).
export function getWsOrigin() {
  if (!API_BASE_URL) {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}`;
  }
  return API_BASE_URL.replace(/^http/, "ws");
}

// Key used to persist the auth JWT in localStorage. Exported so
// AuthContext can read/write it without duplicating the string.
export const TOKEN_STORAGE_KEY = "pm-dashboard.token";

// Attaches the saved JWT (if any) to every outgoing request.
client.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Normalizes Axios/network errors into a small, predictable shape so
// every page can render the same kind of error state instead of each
// screen having to know about Axios internals.
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status ?? null;
    const detail =
      error.response?.data?.detail ??
      error.message ??
      "Something went wrong talking to the server.";

    return Promise.reject({
      status,
      message: typeof detail === "string" ? detail : "Request failed.",
      isNetworkError: !error.response,
      original: error,
    });
  }
);

export default client;