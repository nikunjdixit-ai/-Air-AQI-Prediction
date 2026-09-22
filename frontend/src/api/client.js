/**
 * AirSense Unified API Client
 * Configures base URL from environment variables with production Render fallback.
 */

// Fallback to live Render backend if no specific environment URL is provided
const DEFAULT_REMOTE_URL = "https://air-aqi-prediction.onrender.com";

export const API_BASE_URL = (() => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl && typeof envUrl === "string" && envUrl.trim() !== "") {
    return envUrl.trim().replace(/\/+$/, "");
  }
  // In development, prefer local server if available, but allow remote fallback
  if (import.meta.env.DEV) {
    return "http://127.0.0.1:5000";
  }
  // Production default
  return DEFAULT_REMOTE_URL;
})();

/**
 * Universal fetch wrapper with timeout and standardized JSON response parsing.
 */
export async function apiRequest(endpoint, options = {}, timeoutMs = 12000) {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const defaultHeaders = {
    "Accept": "application/json",
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
        error: (data && data.message) || `HTTP error ${response.status}: ${response.statusText}`,
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
        ? `Request timed out after ${timeoutMs / 1000}s. Server may be spinning up from cold sleep.`
        : `Network connection error: ${err.message}`,
      data: null,
    };
  }
}
