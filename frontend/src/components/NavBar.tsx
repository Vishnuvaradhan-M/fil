import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function NavBar() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  return (
    <nav className="nav">
      <div className="brand"><Link to="/">Hospital</Link></div>
      <div className="links">
        {user && (
          <>
            <Link to="/shifts">Shifts</Link>
            <Link to="/appointments">Appointments</Link>
            <Link to="/rooms">Rooms</Link>
            <Link to="/ml">ML</Link>
            {(user.role === "admin" || user.role === "hr") && <Link to="/users">Users</Link>}
            <button
              onClick={() => {
                logout();
                nav("/login");
              }}
            >
              Logout
            </button>
          </>
        )}
        {!user && <Link to="/login">Login</Link>}
      </div>
    </nav>
  );
}

