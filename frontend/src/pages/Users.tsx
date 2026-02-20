import React, { useEffect, useState } from "react";
import { apiFetch } from "../api/client";

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("STAFF");

  async function loadUsers() {
    try {
      const d = await apiFetch("/users/");
      setUsers(d);
    } catch (e: any) {
      setError(String(e));
    }
  }

  useEffect(() => {
    loadUsers();
  }, []);

  async function createUser(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await apiFetch("/users/", {
        method: "POST",
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          role,
        }),
      });
      setEmail("");
      setFullName("");
      setPassword("");
      setRole("STAFF");
      await loadUsers();
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function deactivateUser(userId: number) {
    try {
      await apiFetch(`/users/${userId}/deactivate`, { method: "PUT" });
      await loadUsers();
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function resetPassword(userId: number) {
    try {
      await apiFetch(`/users/reset-password/${userId}`, { method: "POST" });
      await loadUsers();
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function resetAll() {
    try {
      await apiFetch("/users/reset-all-passwords", { method: "POST" });
      await loadUsers();
    } catch (err: any) {
      setError(String(err));
    }
  }

  return (
    <div>
      <h1>Users</h1>
      {error && <div className="error">{error}</div>}

      <section className="card">
        <h3>Create User</h3>
        <form onSubmit={createUser}>
          <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <input placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          <input placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="ADMIN">ADMIN</option>
            <option value="HR">HR</option>
            <option value="DOCTOR">DOCTOR</option>
            <option value="STAFF">STAFF</option>
          </select>
          <button type="submit">Create</button>
        </form>
        <button onClick={resetAll} style={{ marginTop: 8 }}>Reset All Passwords</button>
      </section>

      <section className="card">
        <h3>All Users</h3>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Full name</th>
              <th>Role</th>
              <th>Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.id}</td>
                <td>{u.email}</td>
                <td>{u.full_name}</td>
                <td>{u.role}</td>
                <td>{String(u.is_active)}</td>
                <td>
                  <button onClick={() => deactivateUser(u.id)}>Deactivate</button>{" "}
                  <button onClick={() => resetPassword(u.id)}>Reset Password</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

