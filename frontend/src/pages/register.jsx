import { useState } from "react";
import { apiRequest } from "../api/api";
import { useNavigate } from "react-router-dom";

function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  async function handleRegister() {
    setError("");
    setSuccess("");
    setLoading(true);

    const data = await apiRequest("/register", "POST", {
      email,
      password,
    });

    setLoading(false);

    if (data.detail) {
      setError(data.detail);
      return;
    }

    setSuccess("Registration successful. Please login.");
    setTimeout(() => navigate("/"), 1000);
  }

  return (
    <form
  className="container"
  onSubmit={(e) => {
    e.preventDefault();
    handleRegister();
  }}
    >
  <h2>Register</h2>

  {error && <p className="error">{error}</p>}
  {success && <p className="success">{success}</p>}

  <input
    type="email"
    placeholder="Email"
    value={email}
    onChange={(e) => setEmail(e.target.value)}
  />

  <input
    type="password"
    placeholder="Password"
    value={password}
    onChange={(e) => setPassword(e.target.value)}
  />

  <button type="submit" disabled={loading}>
    {loading ? "Registering..." : "Register"}
  </button>

  <button type="button" onClick={() => navigate("/")}>
    Back to Login
  </button>
    </form>

  );
}

export default Register;
