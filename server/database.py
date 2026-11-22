"""SQLite storage. Transactions are short; only locally bound demo server is supported."""
from __future__ import annotations
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from .catalog import CANDIDATES, CRITERIA

PROJECT_ROOT=Path(__file__).resolve().parents[1]
DB_PATH=Path(os.environ.get("JPO_DATABASE", str(PROJECT_ROOT/"data"/"jpo.sqlite3")))

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DB_PATH,timeout=10)
    db.row_factory=sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("PRAGMA journal_mode=WAL")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

SCHEMA="""
CREATE TABLE IF NOT EXISTS candidates (
  id TEXT PRIMARY KEY, label TEXT NOT NULL, latitude REAL, longitude REAL,
  coordinate_source TEXT, coordinate_verified INTEGER NOT NULL DEFAULT 0,
  identity_verified INTEGER NOT NULL DEFAULT 0, note TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS criteria (
  code TEXT PRIMARY KEY, group_index INTEGER NOT NULL, label TEXT NOT NULL,
  direction TEXT NOT NULL CHECK(direction IN ('Benefit','Cost')),
  unit TEXT NOT NULL, definition TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS measurements (
  candidate_id TEXT NOT NULL REFERENCES candidates(id), code TEXT NOT NULL REFERENCES criteria(code),
  value REAL NOT NULL CHECK(value >= 0), source TEXT NOT NULL,
  period TEXT NOT NULL, origin TEXT NOT NULL CHECK(origin IN ('synthetic','field')),
  checked INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL,
  PRIMARY KEY(candidate_id,code)
);
CREATE TABLE IF NOT EXISTS experts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, origin TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS judgments (
  expert_id INTEGER NOT NULL REFERENCES experts(id) ON DELETE CASCADE,
  level TEXT NOT NULL, pair_i INTEGER NOT NULL, pair_j INTEGER NOT NULL,
  intensity INTEGER NOT NULL CHECK(intensity BETWEEN -9 AND 9 AND intensity != 0),
  PRIMARY KEY(expert_id,level,pair_i,pair_j)
);
CREATE TABLE IF NOT EXISTS observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id TEXT NOT NULL REFERENCES candidates(id),
  pedestrians_hour REAL NOT NULL, peak_15min REAL NOT NULL,
  vehicles_hour REAL NOT NULL, speed_kmh REAL, calibrated INTEGER NOT NULL DEFAULT 0,
  source TEXT NOT NULL, period TEXT NOT NULL, origin TEXT NOT NULL,
  applied INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, mode TEXT NOT NULL,
  dataset_hash TEXT NOT NULL, result_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, action TEXT NOT NULL,
  payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""

def initialize():
    with connect() as db:
        db.executescript(SCHEMA)
        for id,label in CANDIDATES:
            db.execute("INSERT OR IGNORE INTO candidates(id,label,updated_at) VALUES(?,?,?)",(id,label,now()))
        for row in CRITERIA:
            db.execute("INSERT OR IGNORE INTO criteria(code,group_index,label,direction,unit,definition) VALUES(?,?,?,?,?,?)",row)
        db.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('mode','empty')")

def audit(db,action,payload):
    db.execute("INSERT INTO audit(created_at,action,payload) VALUES(?,?,?)",(now(),action,json.dumps(payload,ensure_ascii=False)))

def mode(db):
    r=db.execute("SELECT value FROM settings WHERE key='mode'").fetchone()
    return r[0] if r else 'empty'

def set_mode(db,val):
    db.execute("INSERT INTO settings(key,value) VALUES('mode',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(val,))

def records(db,table,order='rowid'):
    return [dict(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY {order}").fetchall()]