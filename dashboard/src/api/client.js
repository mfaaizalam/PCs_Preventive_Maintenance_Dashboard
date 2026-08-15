import axios from "axios";

// By default this is "" (relative URLs like /api/agent/dashboard).
// In dev, vite.config.js proxies those to VITE_API_BASE_URL so the
// browser only ever talks to the Vite origin (the backend has no
// CORSMiddleware, so calling it directly cross-origin would fail).
// In production, serve this app behind the same reverse proxy that
// routes /api and /health to the backend. If you deploy the frontend
// on a different origin with no proxy in front, set VITE_API_BASE_URL
// to the backend's full URL AND enable CORSMiddleware on the backend
// — that combination is the only way a browser will allow it.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL_DIRECT || "";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
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
