import { useState } from "react";
import { apiRequest } from "../api/api";
import { useNavigate } from "react-router-dom";


function Login({onLogin}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleLogin() {
    setError("");
    setLoading(true);

    const data = await apiRequest("/login", "POST", {
      email,
      password,
    });

    setLoading(false);

    if (data.detail) {
      setError(data.detail);
      return;
    }

    // success
    onLogin(data.access_token);
    alert("Login successful");
    navigate("/chat");
  }

  return (
  <form
  className="container"
  onSubmit={(e) => {
    e.preventDefault();
    handleLogin();
  }}
  >
  <h2>Login</h2>

  {error && <p className="error">{error}</p>}

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
    {loading ? "Logging in..." : "Login"}
  </button>

  <button type="button" onClick={() => navigate("/register")}>
    Register
  </button>
    </form>

  );

}

export default Login;
