const API_URL = "http://localhost:8000";

export function getToken() {
  return localStorage.getItem("token");
}

export async function apiRequest(path, method = "GET", body = null) {
  const headers = {
    "Content-Type": "application/json",
  };

  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(API_URL + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  return res.json();
}
