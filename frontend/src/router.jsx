import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Layout from "./components/layout/Layout";
import Register from "./pages/Register";

const isAuthenticated = () => {
  return !!localStorage.getItem("token");
};

function ProtectedRoute({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        />
        <Route
          path="/"
          element={
            isAuthenticated()
              ? <Navigate to="/chat" replace />
              : <Navigate to="/login" replace />
          }
        />
        <Route
          path="*"
          element={
            isAuthenticated()
              ? <Navigate to="/chat" replace />
              : <Navigate to="/login" replace />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
