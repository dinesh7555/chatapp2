import axios from "axios";

const api = axios.create({
  baseURL: "http://backend:8000",
});

export default api;


export function handleAuthError(res) {
  if (res.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/login";
    throw new Error("Session expired");
  }
}


