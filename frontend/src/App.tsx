import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthProvider";
import LoginPage from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ShiftsPage from "./pages/Shifts";
import UsersPage from "./pages/Users";
import RoomsPage from "./pages/Rooms";
import AppointmentsPage from "./pages/Appointments";
import MlPage from "./pages/ML";
import RAGPage from "./pages/RAG";
import NavBar from "./components/NavBar";

function ProtectedRoute({ children, roles }: { children: JSX.Element; roles?: string[] }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <div>403 Forbidden</div>;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <NavBar />
      <main className="container">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/shifts/*"
            element={
              <ProtectedRoute>
                <ShiftsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/users/*"
            element={
              <ProtectedRoute roles={["admin", "hr"]}>
                <UsersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/rooms/*"
            element={
              <ProtectedRoute>
                <RoomsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/appointments/*"
            element={
              <ProtectedRoute>
                <AppointmentsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/ml/*"
            element={
              <ProtectedRoute>
                <MlPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/rag"
            element={
              <ProtectedRoute>
                <RAGPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </AuthProvider>
  );
}

