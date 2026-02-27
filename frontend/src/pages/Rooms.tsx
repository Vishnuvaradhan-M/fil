import React, { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api/client";
import ErrorAlert from "../components/ErrorAlert";

export default function RoomsPage() {
  const [rooms, setRooms] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [roomNumber, setRoomNumber] = useState("");
  const [name, setName] = useState("");
  const [capacity, setCapacity] = useState<number | "">("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editCapacity, setEditCapacity] = useState<number | "">("");

  // table controls
  const [filterRoom, setFilterRoom] = useState("");
  const [filterName, setFilterName] = useState("");
  const [page, setPage] = useState(0);
  const pageSize = 10;

  async function loadRooms() {
    try {
      const d = await apiFetch("/rooms/");
      setRooms(d || []);
    } catch (e: any) {
      setError(String(e));
    }
  }

  useEffect(() => {
    loadRooms();
  }, []);

  async function createRoom(e: React.FormEvent) {
    e.preventDefault();
    try {
      await apiFetch("/rooms/", { method: "POST", body: JSON.stringify({ room_number: roomNumber, name, capacity: Number(capacity || 0) }) });
      setRoomNumber("");
      setName("");
      setCapacity("");
      await loadRooms();
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function deleteRoom(roomNum: string) {
    if (!confirm("Delete room?")) return;
    try {
      await apiFetch(`/rooms/${roomNum}`, { method: "DELETE" });
      await loadRooms();
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function toggleAvailability(r: any) {
    try {
      await apiFetch(`/rooms/${r.room_number}`, {
        method: "PUT",
        body: JSON.stringify({ is_active: !r.is_active }),
      });
      await loadRooms();
    } catch (err: any) {
      setError(String(err));
    }
  }

  function startEdit(r: any) {
    setEditingId(r.id);
    setEditCapacity(r.capacity ?? r.bed_capacity ?? 1);
  }

  async function saveEdit(room: any) {
    try {
      await apiFetch(`/rooms/${room.room_number}`, {
        method: "PUT",
        body: JSON.stringify({ bed_capacity: Number(editCapacity) }),
      });
      setEditingId(null);
      setEditCapacity("");
      await loadRooms();
    } catch (err: any) {
      setError(String(err));
    }
  }

  const filtered = useMemo(() => {
    return rooms.filter((r) => {
      if (filterRoom && !(String(r.room_number || "").toLowerCase().includes(filterRoom.toLowerCase()))) return false;
      if (filterName && !(String(r.name || r.ward_name || "").toLowerCase().includes(filterName.toLowerCase()))) return false;
      return true;
    });
  }, [rooms, filterRoom, filterName]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const pageData = filtered.slice(page * pageSize, (page + 1) * pageSize);

  return (
    <div style={{ maxWidth: 960, margin: "24px auto", fontFamily: "Inter, Arial, sans-serif" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h1 style={{ margin: 0 }}>Rooms</h1>
      </header>
      {error && <ErrorAlert title="⚠️ Error" message={error} />}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <section style={{ background: "#fff", padding: 20, borderRadius: 8, boxShadow: "0 1px 3px rgba(0,0,0,0.08)" }}>
          <h3 style={{ marginTop: 0 }}>Create Room</h3>
          <form onSubmit={createRoom} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <input placeholder="Room number" value={roomNumber} onChange={(e) => setRoomNumber(e.target.value)} />
            <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
            <input placeholder="Capacity" value={capacity} onChange={(e) => setCapacity(e.target.value ? Number(e.target.value) : "")} />
            <div style={{ display: "flex", gap: 8 }}>
              <button style={{ flex: 1 }} type="submit">Create</button>
            </div>
          </form>
        </section>

        <section style={{ background: "#fff", padding: 20, borderRadius: 8, boxShadow: "0 1px 3px rgba(0,0,0,0.08)" }}>
          <h3 style={{ marginTop: 0 }}>All Rooms</h3>
          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            <input placeholder="Filter room" value={filterRoom} onChange={(e) => { setFilterRoom(e.target.value); setPage(0); }} />
            <input placeholder="Filter name" value={filterName} onChange={(e) => { setFilterName(e.target.value); setPage(0); }} />
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "1px solid #eee" }}>
                <th style={{ padding: "8px 4px" }}>Room</th>
                <th style={{ padding: "8px 4px" }}>Name</th>
                <th style={{ padding: "8px 4px" }}>Capacity</th>
                <th style={{ padding: "8px 4px" }}>Availability</th>
                <th style={{ padding: "8px 4px" }}></th>
              </tr>
            </thead>
            <tbody>
              {pageData.map((r) => (
                <tr key={r.id} style={{ borderBottom: "1px solid #fafafa" }}>
                  <td style={{ padding: "8px 4px" }}>{r.room_number}</td>
                  <td style={{ padding: "8px 4px" }}>{r.name || r.ward_name}</td>
                  <td style={{ padding: "8px 4px", display: "flex", alignItems: "center", gap: 8 }}>
                    {editingId === r.id ? (
                      <>
                        <input
                          value={String(editCapacity)}
                          onChange={(e) => setEditCapacity(e.target.value ? Number(e.target.value) : "")}
                          style={{ width: 80, padding: "6px 8px", borderRadius: 4, border: "1px solid #ddd" }}
                        />
                        <button
                          onClick={() => saveEdit(r)}
                          title="Save"
                          style={{ background: "#1976d2", color: "#fff", border: "none", padding: "6px 10px", borderRadius: 4 }}
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          title="Cancel"
                          style={{ background: "#f0f0f0", border: "none", padding: "6px 8px", borderRadius: 4 }}
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        <span style={{ minWidth: 40, display: "inline-block", fontWeight: 600 }}>{r.capacity ?? r.bed_capacity}</span>
                        <button
                          onClick={() => startEdit(r)}
                          title="Edit capacity"
                          style={{ background: "transparent", border: "none", color: "#1976d2", cursor: "pointer", padding: "4px 8px" }}
                        >
                          ✎
                        </button>
                      </>
                    )}
                  </td>
                  <td style={{ padding: "8px 4px" }}>
                    <button
                      onClick={() => toggleAvailability(r)}
                      style={{
                        background: r.is_active ? "#2e7d32" : "#9e9e9e",
                        color: "#fff",
                        border: "none",
                        padding: "6px 12px",
                        borderRadius: 20,
                        cursor: "pointer",
                        minWidth: 72,
                      }}
                      aria-pressed={!!r.is_active}
                    >
                      {r.is_active ? "Available" : "Unavailable"}
                    </button>
                  </td>
                  <td style={{ padding: "8px 4px" }}>
                    <button onClick={() => deleteRoom(r.room_number)} style={{ background: "#e53935", color: "#fff", border: "none", padding: "6px 10px", borderRadius: 4 }}>
                      Delete
                    </button>
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
    </div>
  );
}

