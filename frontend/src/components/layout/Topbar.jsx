import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

function Topbar({ onMenuClick, sidebarOpen }) {
  const navigate = useNavigate();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  // Close modal on ESC
  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key === "Escape") {
        setShowLogoutConfirm(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <>
      <header className="topbar">
        <button
          className={`menu-btn ${sidebarOpen ? "open" : ""}`}
          onClick={onMenuClick}
        >
          {sidebarOpen ? "✕" : "☰"}
        </button>

        <button
          className="logout-btn"
          onClick={() => setShowLogoutConfirm(true)}
        >
          Logout
        </button>
      </header>

      {/* 🔥 Logout Confirmation Modal */}
      {showLogoutConfirm && (
        <div
          className="logout-backdrop"
          onClick={() => setShowLogoutConfirm(false)}
        >
          <div
            className="logout-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>Log out?</h3>
            <p>Are you sure you want to log out?</p>

            <div className="logout-actions">
              <button
                className="btn-secondary"
                onClick={() => setShowLogoutConfirm(false)}
              >
                Cancel
              </button>
              <button
                className="btn-danger"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Topbar;
