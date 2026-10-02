const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  let payload = null;
  try { payload = await response.json(); } catch {}
  if (!response.ok) throw new Error(payload?.message || `Request failed with status ${response.status}`);
  return payload;
}

export function health() { return request("/health"); }
export function getItems() { return request("/items"); }
export function createItem(item) { return request("/items", { method: "POST", body: JSON.stringify(item) }); }
export function updateItem(id, patch) { return request(`/items/${id}`, { method: "PATCH", body: JSON.stringify(patch) }); }
export function deleteItem(id) { return request(`/items/${id}`, { method: "DELETE" }); }
export function getSpaces() { return request("/spaces"); }
export function createSpace(space) { return request("/spaces", { method: "POST", body: JSON.stringify(space) }); }
export function updateSpace(id, patch) { return request(`/spaces/${id}`, { method: "PATCH", body: JSON.stringify(patch) }); }
export function deleteSpace(id) { return request(`/spaces/${id}`, { method: "DELETE" }); }

// Notifications API
export function getNotifications() { return request("/notifications"); }
export function createNotification(payload) { return request("/notifications", { method: "POST", body: JSON.stringify(payload) }); }
export function markNotificationRead(id) { return request(`/notifications/${id}/read`, { method: "PATCH" }); }
export function markAllNotificationsRead() { return request("/notifications/read-all", { method: "PATCH" }); }
export function deleteNotification(id) { return request(`/notifications/${id}`, { method: "DELETE" }); }
export function clearAllNotifications() { return request("/notifications/clear-all", { method: "DELETE" }); }
