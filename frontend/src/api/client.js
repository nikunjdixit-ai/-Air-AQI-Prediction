/**
 * AirSense API Client
 *
 * Local development:
 *   React/Vite -> Vite proxy -> Flask at 127.0.0.1:5000
 *
 * Production:
 *   React -> same-origin Flask/Gunicorn
 *
 * VITE_API_BASE_URL can optionally override the API origin.
 */

export const API_BASE_URL = (() => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;

  if (envUrl && typeof envUrl === "string" && envUrl.trim() !== "") {
    return envUrl.trim().replace(/\/+$/, "");
  }

  // Inside Capacitor native Android app, relative URLs resolve to http://localhost
  // on the mobile device. Route to live Render backend by default unless overridden.
  if (
    typeof window !== "undefined" &&
    window.Capacitor &&
    typeof window.Capacitor.isNativePlatform === "function" &&
    window.Capacitor.isNativePlatform()
  ) {
    return "https://air-aqi-prediction.onrender.com";
  }

  // Empty base URL means:
  // - Local development: Vite proxy handles /api requests.
  // - Production website: Flask/Gunicorn handles same-origin requests.
  return "";
})();

/**
 * Universal fetch wrapper with timeout and standardized JSON parsing.
 */
export async function apiRequest(endpoint, options = {}, timeoutMs = 30000) {
  const normalizedEndpoint = endpoint.startsWith("/")
    ? endpoint
    : `/${endpoint}`;

  const url = `${API_BASE_URL}${normalizedEndpoint}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const defaultHeaders = {
    Accept: "application/json",
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers: defaultHeaders,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      return {
        success: false,
        status: response.status,
        error:
          (data && (data.message || data.error)) ||
          `HTTP error ${response.status}: ${response.statusText}`,
        data,
      };
    }

    return {
      success: true,
      status: response.status,
      data,
    };
  } catch (err) {
    clearTimeout(timeoutId);

    const isTimeout = err.name === "AbortError";

    return {
      success: false,
      status: 0,
      error: isTimeout
        ? `Request timed out after ${timeoutMs / 1000}s.`
        : `Network connection error: ${err.message}`,
      data: null,
    };
  }
}