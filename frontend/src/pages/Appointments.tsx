import React, { useEffect, useState } from "react";
import { apiFetch } from "../api/client";

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [patientId, setPatientId] = useState<number | "">("");
  const [doctorId, setDoctorId] = useState<number | "">("");
  const [roomId, setRoomId] = useState<number | "">("");
  const [date, setDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");

  async function loadAppointments() {
    try {
      const d = await apiFetch("/appointments/");
      setAppointments(d);
    } catch (e: any) {
      setError(String(e));
    }
  }

  useEffect(() => {
    loadAppointments();
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
        }),
      });
      setPatientId("");
      setDoctorId("");
      setRoomId("");
      setDate("");
      setStartTime("");
      setEndTime("");
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

  return (
    <div>
      <h1>Appointments</h1>
      {error && <div className="error">{error}</div>}

      <section className="card">
        <h3>Create Appointment</h3>
        <form onSubmit={createAppointment}>
          <input placeholder="Patient ID" value={patientId} onChange={(e) => setPatientId(e.target.value ? Number(e.target.value) : "")} />
          <input placeholder="Doctor ID" value={doctorId} onChange={(e) => setDoctorId(e.target.value ? Number(e.target.value) : "")} />
          <input placeholder="Room ID" value={roomId} onChange={(e) => setRoomId(e.target.value ? Number(e.target.value) : "")} />
          <input placeholder="Date (YYYY-MM-DD)" value={date} onChange={(e) => setDate(e.target.value)} />
          <input placeholder="Start time (HH:MM)" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
          <input placeholder="End time (HH:MM)" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
          <button type="submit">Create</button>
        </form>
      </section>

      <section className="card">
        <h3>Appointments</h3>
        <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Patient</th>
            <th>Staff</th>
            <th>Room</th>
            <th>Start</th>
            <th>End</th>
          </tr>
        </thead>
        <tbody>
          {appointments.map((a) => (
            <tr key={a.id}>
              <td>{a.id}</td>
              <td>{a.patient_id}</td>
              <td>{a.staff_id}</td>
              <td>{a.room_id}</td>
              <td>{a.start_time}</td>
              <td>{a.end_time}</td>
              <td><button onClick={() => cancelAppointment(a.id)}>Cancel</button></td>
            </tr>
          ))}
        </tbody>
      </table>
      </section>

      <section className="card">
        <h3>Set Availability</h3>
        <form onSubmit={createAvailability}>
          <input placeholder="Doctor ID" value={doctorId} onChange={(e) => setDoctorId(e.target.value ? Number(e.target.value) : "")} />
          <input placeholder="Date (YYYY-MM-DD)" value={date} onChange={(e) => setDate(e.target.value)} />
          <input placeholder="Start time" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
          <input placeholder="End time" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
          <button type="submit">Set Availability</button>
        </form>
      </section>
    </div>
  );
}

