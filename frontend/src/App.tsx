import { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import { EditMode } from "./pages/EditMode";
import { PresentMode } from "./pages/PresentMode";
import { Login } from "./pages/Login";
import { Edit3, Play, LogOut } from "lucide-react";
import "./App.css";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    console.log("App mounted");
    // Check if user is already authenticated
    const authStatus = localStorage.getItem("authenticated");
    if (authStatus === "true") {
      setIsAuthenticated(true);
    }
    setIsCheckingAuth(false);
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("authenticated");
    setIsAuthenticated(false);
  };

  if (isCheckingAuth) {
    return <div className="app-container">Loading...</div>;
  }

  return (
    <Router>
      <div className="app-container">
        <nav className="nav-bar">
          <div className="nav-logo">Beautiful Moments</div>
          <div className="nav-links">
            <Link to="/edit" className="nav-link">
              <Edit3 size={18} /> Edit
            </Link>
            <Link to="/present" className="nav-link">
              <Play size={18} /> Present
            </Link>
            {isAuthenticated && (
              <button onClick={handleLogout} className="nav-link nav-logout">
                <LogOut size={18} /> Logout
              </button>
            )}
          </div>
        </nav>

        <Routes>
          <Route
            path="/edit"
            element={
              isAuthenticated ? <EditMode /> : <Login onLogin={handleLogin} />
            }
          />
          <Route path="/present" element={<PresentMode />} />
          <Route path="/" element={<Navigate to="/present" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

