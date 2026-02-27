import React, { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/AuthProvider";
import ErrorAlert from "../components/ErrorAlert";

type Shift = any;

export default function ShiftsPage() {
  const { user } = useAuth();
  const isAdmin = String(user?.role || "").toLowerCase() === "admin";

  const [shifts, setShifts] = useState<Shift[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [shiftDate, setShiftDate] = useState("");
  const [name, setName] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [type, setType] = useState("MORNING");

  const [assignStaffId, setAssignStaffId] = useState<number | "">("");
  const [assignShiftId, setAssignShiftId] = useState<number | "">("");

  const [myShifts, setMyShifts] = useState<any[]>([]);
  const [swapAssignmentId, setSwapAssignmentId] = useState<number | "">("");
  const [swapTargetStaffId, setSwapTargetStaffId] = useState<number | "">("");

  // table controls
  const [filterName, setFilterName] = useState("");
  const [filterType, setFilterType] = useState("");
  const [page, setPage] = useState(0);
  const pageSize = 10;

  async function loadShifts() {
    try {
      const d = await apiFetch("/shifts/");
      setShifts(d || []);
    } catch (e: any) {
      setError(String(e));
    }
  }

  async function loadMyShifts() {
    try {
      const d = await apiFetch("/shifts/my-shifts");
      setMyShifts(d || []);
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    loadShifts();
    loadMyShifts();
    if (isAdmin) {
      loadSwapRequests();
    }
  }, []);

  const [swapRequests, setSwapRequests] = useState<any[]>([]);

  async function loadSwapRequests() {
    try {
      const d = await apiFetch("/shifts/swap/requests");
      setSwapRequests(d || []);
    } catch {
      // endpoint might not exist or none pending — ignore
      setSwapRequests([]);
    }
  }

  async function createShift(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    // basic validation
    if (!shiftDate) {
      setError("Please choose a date for the shift.");
      return;
    }
    if (!startTime || !endTime) {
      setError("Please provide both start and end times.");
      return;
    }
    // normalize times to HH:MM:SS
    const norm = (t: string) => {
      if (!t) return t;
      const parts = t.split(":");
      if (parts.length === 2) return `${parts[0].padStart(2,"0")}:${parts[1].padStart(2,"0")}:00`;
      return t;
    };
    const sISO = `${shiftDate}T${norm(startTime)}`;
    const eISO = `${shiftDate}T${norm(endTime)}`;
    try {
      await apiFetch("/shifts/", {
        method: "POST",
        // send same keys as backend expects; values include date portion to be compatible
        body: JSON.stringify({ name, start_time: sISO, end_time: eISO, type }),
      });
      setName("");
      setStartTime("");
      setShiftDate("");
      setEndTime("");
      setType("MORNING");
      await loadShifts();
      setSuccessMessage("Shift created successfully.");
    } catch (err: any) {
      setError(err?.message ?? String(err));
    }
  }

  async function updateShift(id: number) {
    const newName = prompt("New name");
    if (!newName) return;
    try {
      await apiFetch(`/shifts/${id}`, { method: "PUT", body: JSON.stringify({ name: newName }) });
      await loadShifts();
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function deleteShift(id: number) {
    if (!confirm("Delete shift?")) return;
    try {
      await apiFetch(`/shifts/${id}`, { method: "DELETE" });
      await loadShifts();
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function assignShift(e: React.FormEvent) {
    e.preventDefault();
    try {
      await apiFetch("/shifts/assign", { method: "POST", body: JSON.stringify({ staff_id: Number(assignStaffId), shift_id: Number(assignShiftId), status: "ASSIGNED" }) });
      setAssignStaffId("");
      setAssignShiftId("");
      await loadShifts();
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function requestSwap(e: React.FormEvent) {
    e.preventDefault();
    try {
      await apiFetch("/shifts/swap", { method: "POST", body: JSON.stringify({ assignment_id: Number(swapAssignmentId), target_staff_id: Number(swapTargetStaffId) }) });
      setSwapAssignmentId("");
      setSwapTargetStaffId("");
      await loadMyShifts();
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function approveSwap(id: number) {
    if (!confirm("Approve swap?")) return;
    try {
      await apiFetch(`/shifts/swap/approve/${id}`, { method: "POST" });
      await loadMyShifts();
      await loadShifts();
      await loadSwapRequests();
      setSuccessMessage("Swap approved.");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError(err?.message ?? String(err));
    }
  }

  async function rejectSwap(id: number) {
    if (!confirm("Reject swap?")) return;
    try {
      await apiFetch(`/shifts/swap/reject/${id}`, { method: "POST" });
      await loadSwapRequests();
      setSuccessMessage("Swap rejected.");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError(err?.message ?? String(err));
    }
  }

  const filtered = useMemo(() => {
    return shifts.filter((s) => {
      if (filterName && !(String(s.name || "").toLowerCase().includes(filterName.toLowerCase()))) return false;
      if (filterType && !(String(s.type || "").toLowerCase().includes(filterType.toLowerCase()))) return false;
      return true;
    });
  }, [shifts, filterName, filterType]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const pageData = filtered.slice(page * pageSize, (page + 1) * pageSize);

  function humanShiftType(t: string) {
    if (!t) return "";
    const v = String(t).toLowerCase();
    if (v.includes("mor")) return "Morning";
    if (v.includes("after") || v.includes("eve")) return "Afternoon";
    if (v.includes("night")) return "Night";
    return t;
  }

  return (
    <div>
      <h1>Shifts</h1>
      {error && <ErrorAlert title="⚠️ Error" message={error} />}
      <section className="card">
        <h3>Create Shift</h3>
        <form onSubmit={createShift} style={{ display: "flex", gap: 8, flexDirection: "column" }}>
          <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
              <label style={{ fontSize: 12, color: "var(--muted)" }}>Date</label>
              <input type="date" value={shiftDate} onChange={(e) => setShiftDate(e.target.value)} />
            </div>
            <div style={{ display: "flex", flexDirection: "column", width: 180 }}>
              <label style={{ fontSize: 12, color: "var(--muted)" }}>Start Time</label>
              <input type="time" step="1" placeholder="Start time" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
            </div>
            <div style={{ display: "flex", flexDirection: "column", width: 180 }}>
              <label style={{ fontSize: 12, color: "var(--muted)" }}>End Time</label>
              <input type="time" step="1" placeholder="End time" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
            </div>
          </div>
          <select value={type} onChange={(e) => setType(e.target.value)}>
            <option value="MORNING">MORNING</option>
            <option value="AFTERNOON">AFTERNOON</option>
            <option value="NIGHT">NIGHT</option>
          </select>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <button type="submit">Create</button>
            {successMessage && <div style={{ padding: "8px 12px", background: "#edfbe9", borderRadius: 8, color: "#1b5e20" }}>{successMessage}</div>}
          </div>
        </form>
      </section>

      <section className="card">
        <h3>Assign Staff</h3>
        <form onSubmit={assignShift}>
          <input placeholder="Staff ID" value={assignStaffId} onChange={(e) => setAssignStaffId(e.target.value ? Number(e.target.value) : "")} />
          <input placeholder="Shift ID" value={assignShiftId} onChange={(e) => setAssignShiftId(e.target.value ? Number(e.target.value) : "")} />
          <button type="submit">Assign</button>
        </form>
      </section>

      <div style={{ marginTop: 12 }} className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <h3 style={{ margin: 0 }}>Shifts</h3>
          <div style={{ display: "flex", gap: 8 }}>
            <input placeholder="Filter name" value={filterName} onChange={(e) => { setFilterName(e.target.value); setPage(0); }} />
            <input placeholder="Filter type" value={filterType} onChange={(e) => { setFilterType(e.target.value); setPage(0); }} />
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Start</th>
              <th>End</th>
              <th>Shift Type</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {pageData.map((s) => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.name}</td>
                <td>{s.start_time}</td>
                <td>{s.end_time}</td>
                <td>{humanShiftType(s.type)}</td>
                <td>
                  <button onClick={() => updateShift(s.id)}>Edit</button>{" "}
                  <button onClick={() => deleteShift(s.id)}>Delete</button>
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
      </div>

      {!isAdmin && (
        <section className="card" style={{ marginTop: 12 }}>
          <h3>My Shifts</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Staff</th>
                <th>Shift</th>
                <th>Status</th>
                <th>Target</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {myShifts.map((a) => (
                <tr key={a.id}>
                  <td>{a.id}</td>
                  <td>{a.staff_id}</td>
                  <td>{a.shift_id}</td>
                  <td>{a.status}</td>
                  <td>{a.target_staff_id ?? "-"}</td>
                  <td>
                    {a.status === "SWAP_REQUESTED" && isAdmin && <button onClick={() => approveSwap(a.id)}>Approve</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {!isAdmin && (
        <section className="card" style={{ marginTop: 12 }}>
          <h3>Request Swap</h3>
          <form onSubmit={requestSwap}>
            <input placeholder="Your assignment ID" value={swapAssignmentId} onChange={(e) => setSwapAssignmentId(e.target.value ? Number(e.target.value) : "")} />
            <input placeholder="Target staff ID" value={swapTargetStaffId} onChange={(e) => setSwapTargetStaffId(e.target.value ? Number(e.target.value) : "")} />
            <button type="submit">Request Swap</button>
          </form>
        </section>
      )}
      {isAdmin && (
        <section className="card" style={{ marginTop: 12 }}>
          <h3>Swap Approvals</h3>
          {swapRequests.length === 0 ? (
            <div style={{ color: "var(--muted)" }}>No pending swap requests.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Assignment</th>
                  <th>Requester</th>
                  <th>Target</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {swapRequests.map((r) => (
                  <tr key={r.id}>
                    <td>{r.id}</td>
                    <td>{r.assignment_id}</td>
                    <td>{r.requester_id}</td>
                    <td>{r.target_staff_id}</td>
                    <td style={{ display: "flex", gap: 8 }}>
                      <button onClick={() => approveSwap(r.id)}>Approve</button>
                      <button onClick={() => rejectSwap(r.id)} style={{ background: "#e53935", color: "#fff", border: "none", padding: "6px 10px", borderRadius: 6 }}>
                        Reject
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}
    </div>
  );
}

