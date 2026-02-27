import React, { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api/client";
import ErrorAlert from "../components/ErrorAlert";

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("STAFF");

  // table controls
  const [filterEmail, setFilterEmail] = useState("");
  const [filterName, setFilterName] = useState("");
  const [filterRole, setFilterRole] = useState("");
  const [page, setPage] = useState(0);
  const pageSize = 10;

  async function loadUsers() {
    try {
      const d = await apiFetch("/users/");
      setUsers(d || []);
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
          role: String(role).toLowerCase(),
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

  // Removed individual reset password and reset-all UI per requirement.

  const filtered = useMemo(() => {
    return users.filter((u) => {
      if (filterEmail && !(u.email || "").toLowerCase().includes(filterEmail.toLowerCase())) return false;
      if (filterName && !(u.full_name || "").toLowerCase().includes(filterName.toLowerCase())) return false;
      if (filterRole && !(String(u.role || "").toLowerCase().includes(filterRole.toLowerCase()))) return false;
      return true;
    });
  }, [users, filterEmail, filterName, filterRole]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const pageData = filtered.slice(page * pageSize, (page + 1) * pageSize);

  return (
    <div>
      <h1>Users</h1>
      {error && <ErrorAlert title="⚠️ Error" message={error} />}

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
      </section>

      <section className="card">
        <h3>All Users</h3>
        <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
          <input placeholder="Filter email" value={filterEmail} onChange={(e) => { setFilterEmail(e.target.value); setPage(0); }} />
          <input placeholder="Filter name" value={filterName} onChange={(e) => { setFilterName(e.target.value); setPage(0); }} />
          <input placeholder="Filter role" value={filterRole} onChange={(e) => { setFilterRole(e.target.value); setPage(0); }} />
        </div>
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
            {pageData.map((u) => (
              <tr key={u.id}>
                <td>{u.id}</td>
                <td>{u.email}</td>
                <td>{u.full_name}</td>
                <td>{u.role}</td>
                <td>{String(u.is_active)}</td>
                <td>
                  <button onClick={() => deactivateUser(u.id)}>Deactivate</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8, alignItems: "center" }}>
          <div style={{ color: "var(--muted)" }}>Showing {pageData.length} of {filtered.length}</div>
          <div>
            <button className="page-btn" onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}>Previous</button>
            <button className="page-btn" onClick={() => setPage(Math.min(totalPages - 1, page + 1))} disabled={page >= totalPages - 1} style={{ marginLeft: 8 }}>Next</button>
          </div>
        </div>
      </section>
    </div>
  );
}

