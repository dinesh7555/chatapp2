import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState } from "react";
import Login from "./pages/Login";
import Chat from "./pages/Chat";
import Register from "./pages/register";

function App() {
  
  const [token, setToken] = useState(localStorage.getItem("token"));

  function handleLogin(token) {
    localStorage.setItem("token", token);
    setToken(token);
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setToken(null);
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            token ? (
              <Navigate to="/chat" />
            ) : (
              <Login onLogin={handleLogin} />
            )
          }
        />
        
        <Route
          path="/register"
          element={token ? <Navigate to="/chat" /> : <Register />}
        />
        <Route
          path="/chat"
          element={
            token ? (
              <Chat onLogout={handleLogout} />
            ) : (
              <Navigate to="/" />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
