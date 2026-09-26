/**
 * AirSense Location Service Adapter
 *
 * Isolates browser geolocation (`navigator.geolocation`) behind a platform-agnostic
 * interface so UI components do not depend on browser-specific APIs directly.
 * Can be replaced cleanly with `expo-location` or `@capacitor/geolocation` on mobile.
 */

export const CURRENT_LOCATION_VALUE = "__current_location__";

let cachedCoords = null;
let cachedTimestamp = 0;
const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes

/**
 * Request the user's current geographic coordinates once per session TTL.
 *
 * @param {Object} options
 * @param {number} [options.timeoutMs=8000]
 * @param {boolean} [options.forceRefresh=false]
 * @returns {Promise<{
 *   supported: boolean,
 *   granted: boolean,
 *   latitude?: number,
 *   longitude?: number,
 *   accuracy?: number,
 *   reason?: string,
 *   message?: string
 * }>}
 */
export async function getCurrentLocation({
  timeoutMs = 8000,
  forceRefresh = false,
} = {}) {
  if (
    !forceRefresh &&
    cachedCoords &&
    Date.now() - cachedTimestamp < CACHE_TTL_MS
  ) {
    return {
      supported: true,
      granted: true,
      ...cachedCoords,
    };
  }

  if (typeof navigator === "undefined" || !("geolocation" in navigator)) {
    return {
      supported: false,
      granted: false,
      reason: "unsupported",
      message: "Location access is unavailable. Showing the selected city.",
    };
  }

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coords = {
          latitude: Number(position.coords.latitude.toFixed(4)),
          longitude: Number(position.coords.longitude.toFixed(4)),
          accuracy: position.coords.accuracy,
        };
        cachedCoords = coords;
        cachedTimestamp = Date.now();
        resolve({
          supported: true,
          granted: true,
          ...coords,
        });
      },
      (err) => {
        let reason = "unavailable";
        if (err && err.code === 1) {
          reason = "permission_denied";
        } else if (err && err.code === 3) {
          reason = "timeout";
        }
        resolve({
          supported: true,
          granted: false,
          reason,
          message: "Location access is unavailable. Showing the selected city.",
        });
      },
      {
        enableHighAccuracy: false,
        timeout: timeoutMs,
        maximumAge: CACHE_TTL_MS,
      }
    );
  });
}
