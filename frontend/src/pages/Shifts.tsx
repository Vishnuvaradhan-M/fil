import React, { useEffect, useState } from "react";
import { apiFetch } from "../api/client";

type Shift = any;

export default function ShiftsPage() {
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [type, setType] = useState("MORNING");

  const [assignStaffId, setAssignStaffId] = useState<number | "">("");
  const [assignShiftId, setAssignShiftId] = useState<number | "">("");

  const [myShifts, setMyShifts] = useState<any[]>([]);
  const [swapAssignmentId, setSwapAssignmentId] = useState<number | "">("");
  const [swapTargetStaffId, setSwapTargetStaffId] = useState<number | "">("");

  async function loadShifts() {
    try {
      const d = await apiFetch("/shifts/");
      setShifts(d);
    } catch (e: any) {
      setError(String(e));
    }
  }

  async function loadMyShifts() {
    try {
      const d = await apiFetch("/shifts/my-shifts");
      setMyShifts(d);
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    loadShifts();
    loadMyShifts();
  }, []);

  async function createShift(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await apiFetch("/shifts/", {
        method: "POST",
        body: JSON.stringify({ name, start_time: startTime, end_time: endTime, type }),
      });
      setName("");
      setStartTime("");
      setEndTime("");
      setType("MORNING");
      await loadShifts();
    } catch (err: any) {
      setError(String(err));
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
    } catch (err: any) {
      setError(String(err));
    }
  }

  return (
    <div>
      <h1>Shifts</h1>
      {error && <div className="error">{error}</div>}
      <section className="card">
        <h3>Create Shift</h3>
        <form onSubmit={createShift}>
          <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
          <input placeholder="Start time (ISO)" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
          <input placeholder="End time (ISO)" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
          <select value={type} onChange={(e) => setType(e.target.value)}>
            <option value="MORNING">MORNING</option>
            <option value="AFTERNOON">AFTERNOON</option>
            <option value="NIGHT">NIGHT</option>
          </select>
          <button type="submit">Create</button>
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

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Start</th>
            <th>End</th>
            <th>Type</th>
          </tr>
        </thead>
        <tbody>
          {shifts.map((s) => (
            <tr key={s.id}>
              <td>{s.id}</td>
              <td>{s.name}</td>
              <td>{s.start_time}</td>
              <td>{s.end_time}</td>
              <td>{s.type}</td>
              <td>
                <button onClick={() => updateShift(s.id)}>Edit</button>{" "}
                <button onClick={() => deleteShift(s.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <section className="card">
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
                  {a.status === "SWAP_REQUESTED" && <button onClick={() => approveSwap(a.id)}>Approve</button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="card">
        <h3>Request Swap</h3>
        <form onSubmit={requestSwap}>
          <input placeholder="Your assignment ID" value={swapAssignmentId} onChange={(e) => setSwapAssignmentId(e.target.value ? Number(e.target.value) : "")} />
          <input placeholder="Target staff ID" value={swapTargetStaffId} onChange={(e) => setSwapTargetStaffId(e.target.value ? Number(e.target.value) : "")} />
          <button type="submit">Request Swap</button>
        </form>
      </section>
    </div>
  );
}

