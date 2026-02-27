import React, { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api/client";
import ErrorAlert from "../components/ErrorAlert";

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [patientId, setPatientId] = useState<number | "">("");
  const [doctorId, setDoctorId] = useState<number | "">("");
  const [roomId, setRoomId] = useState<number | "">("");
  const [date, setDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [patientName, setPatientName] = useState("");
  const [patientPhone, setPatientPhone] = useState("");
  const [patientAge, setPatientAge] = useState<number | "">("");
  const [patientGender, setPatientGender] = useState("");
  const [reason, setReason] = useState("");
  const [rooms, setRooms] = useState<any[]>([]);
  const [doctors, setDoctors] = useState<Record<number, string>>({});
  const [appointmentType, setAppointmentType] = useState("Consultation");

  // table controls
  const [filterPatient, setFilterPatient] = useState("");
  const [filterDoctor, setFilterDoctor] = useState("");
  const [filterDate, setFilterDate] = useState("");
  const [page, setPage] = useState(0);
  const pageSize = 10;

  async function loadAppointments() {
    setLoading(true);
    setError(null);
    try {
      const d = await apiFetch("/appointments/");
      setAppointments(d || []);
    } catch (e: any) {
      // show useful error text
      setError(e?.message || String(e));
    } finally {
      setLoading(false);
    }
  }
  async function loadRooms() {
    try {
      const r = await apiFetch("/rooms/");
      setRooms(r);
    } catch (e: any) {
      // ignore
    }
  }
  async function loadDoctors() {
    try {
      const list = await apiFetch("/users/?skip=0&limit=200");
      const map: Record<number, string> = {};
      if (Array.isArray(list)) {
        list.forEach((u: any) => {
          if (u && u.id) map[u.id] = u.full_name || u.email || String(u.id);
        });
      }
      setDoctors(map);
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    loadAppointments();
    loadRooms();
    loadDoctors();
  }, []);

  async function createAppointment(e: React.FormEvent) {
    e.preventDefault();
    try {
      await apiFetch("/appointments/", {
        method: "POST",
        body: JSON.stringify({
          patient_id: Number(patientId),
          doctor_id: Number(doctorId),
          room_id: Number(roomId),
          appointment_date: date,
          start_time: startTime,
          end_time: endTime,
          patient_name: patientName,
          patient_phone: patientPhone,
          patient_age: Number(patientAge || 0),
          patient_gender: patientGender,
          appointment_type: appointmentType,
          reason_for_visit: reason,
        }),
      });
      setPatientId("");
      setDoctorId("");
      setRoomId("");
      setDate("");
      setStartTime("");
      setEndTime("");
      setPatientName("");
      setPatientPhone("");
      setPatientAge("");
      setPatientGender("");
      setReason("");
      await loadAppointments();
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function cancelAppointment(id: number) {
    if (!confirm("Cancel appointment?")) return;
    try {
      await apiFetch(`/appointments/${id}`, { method: "DELETE" });
      await loadAppointments();
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function createAvailability(e: React.FormEvent) {
    e.preventDefault();
    try {
      await apiFetch("/appointments/availability", {
        method: "POST",
        body: JSON.stringify({
          doctor_id: Number(doctorId),
          date,
          start_time: startTime,
          end_time: endTime,
        }),
      });
    } catch (err: any) {
      setError(String(err));
    }
  }

  const filtered = useMemo(() => {
    return appointments.filter((a) => {
      if (filterPatient && !(String(a.patient_name || a.patient_id || "").toLowerCase().includes(filterPatient.toLowerCase()))) return false;
      if (filterDoctor && !(String(doctors[a.doctor_id] || a.doctor_id).toLowerCase().includes(filterDoctor.toLowerCase()))) return false;
      if (filterDate && !(String(a.appointment_date || a.appointment_date || "").includes(filterDate))) return false;
      return true;
    });
  }, [appointments, filterPatient, filterDoctor, filterDate, doctors]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const pageData = filtered.slice(page * pageSize, (page + 1) * pageSize);

  return (
    <div style={{ maxWidth: 980, margin: "20px auto", fontFamily: "Inter, Arial, sans-serif" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <h1 style={{ margin: 0 }}>Appointments</h1>
      </header>
      {error && <ErrorAlert title="⚠️ Error" message={error} />}

      <div style={{ display: "grid", gridTemplateColumns: "360px 1fr", gap: 20 }}>
        <section style={{ background: "#fff", padding: 20, borderRadius: 8, boxShadow: "0 1px 3px rgba(0,0,0,0.04)" }}>
          <h3 style={{ marginTop: 0 }}>Create Appointment</h3>
          <form onSubmit={createAppointment} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <input placeholder="Patient ID" value={patientId} onChange={(e) => setPatientId(e.target.value ? Number(e.target.value) : "")} />
            <input placeholder="Patient Name" value={patientName} onChange={(e) => setPatientName(e.target.value)} />
            <input placeholder="Patient Phone" value={patientPhone} onChange={(e) => setPatientPhone(e.target.value)} />
            <input placeholder="Patient Age" value={patientAge} onChange={(e) => setPatientAge(e.target.value ? Number(e.target.value) : "")} />
            <select value={patientGender} onChange={(e) => setPatientGender(e.target.value)}>
              <option value="">Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
            <input placeholder="Doctor ID" value={doctorId} onChange={(e) => setDoctorId(e.target.value ? Number(e.target.value) : "")} />
            <select value={roomId} onChange={(e) => setRoomId(e.target.value ? Number(e.target.value) : "")}>
              <option value="">Select Room</option>
              {rooms.map((r) => <option key={r.id} value={r.id}>{r.room_number} — {r.name ?? r.ward_name}</option>)}
            </select>
            <input type="date" placeholder="Date (YYYY-MM-DD)" value={date} onChange={(e) => setDate(e.target.value)} />
            <input type="time" step="1" placeholder="Start time (HH:MM)" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
            <input type="time" step="1" placeholder="End time (HH:MM)" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
            <select value={appointmentType} onChange={(e) => setAppointmentType(e.target.value)}>
              <option value="Consultation">Consultation</option>
              <option value="Follow-up">Follow-up</option>
              <option value="Review">Review</option>
              <option value="Emergency">Emergency</option>
            </select>
            <input placeholder="Reason for visit" value={reason} onChange={(e) => setReason(e.target.value)} />
            <button type="submit" style={{ marginTop: 6 }}>Create</button>
          </form>
        </section>

        <section style={{ background: "#fff", padding: 20, borderRadius: 8, boxShadow: "0 1px 3px rgba(0,0,0,0.04)" }}>
          <h3 style={{ marginTop: 0 }}>Appointments</h3>
          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            <input placeholder="Filter patient" value={filterPatient} onChange={(e) => { setFilterPatient(e.target.value); setPage(0); }} />
            <input placeholder="Filter doctor" value={filterDoctor} onChange={(e) => { setFilterDoctor(e.target.value); setPage(0); }} />
            <input type="date" placeholder="Filter date" value={filterDate} onChange={(e) => { setFilterDate(e.target.value); setPage(0); }} />
          </div>
          {loading ? (
            <div>Loading...</div>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ textAlign: "left", borderBottom: "1px solid #eee" }}>
                  <th style={{ padding: "8px 6px" }}>ID</th>
                  <th style={{ padding: "8px 6px" }}>Patient</th>
                  <th style={{ padding: "8px 6px" }}>Age</th>
                  <th style={{ padding: "8px 6px" }}>Gender</th>
                  <th style={{ padding: "8px 6px" }}>Doctor</th>
                  <th style={{ padding: "8px 6px" }}>Room</th>
                  <th style={{ padding: "8px 6px" }}>Start</th>
                  <th style={{ padding: "8px 6px" }}>End</th>
                  <th style={{ padding: "8px 6px" }}></th>
                </tr>
              </thead>
              <tbody>
                {pageData.map((a) => (
                  <tr key={a.id} style={{ borderBottom: "1px solid #fafafa" }}>
                    <td style={{ padding: "8px 6px" }}>{a.id}</td>
                    <td style={{ padding: "8px 6px" }}>{a.patient_name ?? a.patient_id}</td>
                    <td style={{ padding: "8px 6px" }}>{a.patient_age}</td>
                    <td style={{ padding: "8px 6px" }}>{a.patient_gender}</td>
                    <td style={{ padding: "8px 6px" }}>{doctors[a.doctor_id] ?? a.doctor_id}</td>
                    <td style={{ padding: "8px 6px" }}>{a.room_name ?? a.room_id}</td>
                    <td style={{ padding: "8px 6px" }}>{a.start_time}</td>
                    <td style={{ padding: "8px 6px" }}>{a.end_time}</td>
                    <td style={{ padding: "8px 6px" }}><button onClick={() => cancelAppointment(a.id)}>Cancel</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
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

