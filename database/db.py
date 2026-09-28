import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class Database:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            connection.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL, voltage REAL NOT NULL, current REAL NOT NULL,
                    temperature REAL NOT NULL, device_load REAL NOT NULL,
                    soc REAL NOT NULL, soh REAL NOT NULL, power REAL NOT NULL,
                    energy_consumed REAL NOT NULL, predicted_runtime REAL NOT NULL,
                    power_mode TEXT NOT NULL, source TEXT NOT NULL,
                    session_id TEXT NOT NULL, model_status TEXT NOT NULL,
                    details TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS telemetry_stream ON telemetry(source, session_id, id);
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
                    message TEXT NOT NULL, level TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL);
            """)

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def load_state(self):
        with self.connection() as connection:
            row = connection.execute("SELECT value FROM state WHERE id=1").fetchone()
            return json.loads(row[0]) if row else None

    def save(self, state, events, reading=None):
        with self.connection() as connection:
            if reading is not None:
                fields = ["timestamp", "voltage", "current", "temperature", "device_load", "soc", "soh",
                          "power", "energy_consumed", "predicted_runtime", "power_mode", "source",
                          "session_id", "model_status"]
                cursor = connection.execute(
                    f"INSERT INTO telemetry ({','.join(fields)},details) VALUES ({','.join(['?'] * 15)})",
                    [reading[key] for key in fields] + [json.dumps(reading, allow_nan=False)])
                reading["id"] = cursor.lastrowid
                state["latest"] = reading
            connection.executemany("INSERT INTO events(timestamp,message,level) VALUES (?,?,?)", events)
            connection.execute("INSERT INTO state(id,value) VALUES (1,?) ON CONFLICT(id) DO UPDATE SET value=excluded.value",
                               (json.dumps(state, allow_nan=False),))
            # Bound disk growth for an unattended college demo (~5.5 h at 2 s/sample).
            connection.execute("DELETE FROM telemetry WHERE id <= (SELECT MAX(id)-10000 FROM telemetry)")
            connection.execute("DELETE FROM events WHERE id <= (SELECT MAX(id)-1000 FROM events)")

    def history(self, source, session_id, limit=60):
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT id, details FROM telemetry WHERE source=? AND session_id=? ORDER BY id DESC LIMIT ?",
                (source, session_id, limit)).fetchall()
            return [{**json.loads(row["details"]), "id": row["id"]} for row in reversed(rows)]

    def events(self, limit=16):
        with self.connection() as connection:
            return [dict(row) for row in connection.execute(
                "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]


if __name__ == "__main__":
    db = Database(Path(__file__).resolve().parents[1] / "data/battery.db")
    print(f"SQLite initialized: {db.path}")
