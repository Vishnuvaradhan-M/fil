import React, { useEffect, useState } from "react";
import { apiFetch } from "../api/client";

export default function RoomsPage() {
  const [rooms, setRooms] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [roomNumber, setRoomNumber] = useState("");
  const [name, setName] = useState("");
  const [capacity, setCapacity] = useState<number | "">("");

  async function loadRooms() {
    try {
      const d = await apiFetch("/rooms/");
      setRooms(d);
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

  return (
    <div>
      <h1>Rooms</h1>
      {error && <div className="error">{error}</div>}

      <section className="card">
        <h3>Create Room</h3>
        <form onSubmit={createRoom}>
          <input placeholder="Room number" value={roomNumber} onChange={(e) => setRoomNumber(e.target.value)} />
          <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
          <input placeholder="Capacity" value={capacity} onChange={(e) => setCapacity(e.target.value ? Number(e.target.value) : "")} />
          <button type="submit">Create</button>
        </form>
      </section>

      <section className="card">
        <h3>All Rooms</h3>
        <ul>
          {rooms.map((r) => (
            <li key={r.id}>
              {r.room_number} — {r.name} (capacity: {r.capacity}){" "}
              <button onClick={() => deleteRoom(r.room_number)}>Delete</button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

