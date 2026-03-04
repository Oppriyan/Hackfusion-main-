import sqlite3
from pathlib import Path

# -------------------------------------------------
# PATH CONFIGURATION
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "pharmacy.db"


# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # -------------------------------------------------
    # MEDICINES TABLE
    # -------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER UNIQUE,
        name TEXT NOT NULL,
        pzn TEXT,
        price REAL,
        package_size TEXT,
        description TEXT,
        stock INTEGER DEFAULT 100,
        prescription_required TEXT DEFAULT "No"
    )
    """)

    # -------------------------------------------------
    # CUSTOMERS TABLE
    # -------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id TEXT PRIMARY KEY,
        age INTEGER,
        gender TEXT
    )
    """)

        # -------------------------------------------------
    # USERS TABLE (AUTH SYSTEM)
    # -------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # -------------------------------------------------
    # ORDERS TABLE
    # -------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        product_name TEXT,
        quantity INTEGER,
        purchase_date TEXT,
        total_price REAL,
        dosage_frequency TEXT,
        prescription_required TEXT
    )
    """)

    # -------------------------------------------------
    # PRESCRIPTIONS TABLE (UPLOAD + APPROVAL SYSTEM)
    # -------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT NOT NULL,
        medicine_id INTEGER NOT NULL,
        file_path TEXT,
        status TEXT DEFAULT 'Pending',
        verified_at TEXT,
        expires_at TEXT,
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(customer_id, medicine_id)
    )
    """)

    # -------------------------------------------------
    # SAFE MIGRATION CHECKS
    # -------------------------------------------------

    # Ensure prescription_required column exists in medicines
    cursor.execute("PRAGMA table_info(medicines)")
    medicine_columns = [col[1] for col in cursor.fetchall()]

    if "prescription_required" not in medicine_columns:
        cursor.execute("""
            ALTER TABLE medicines
            ADD COLUMN prescription_required TEXT DEFAULT "No"
        """)

    # Ensure new columns exist in prescriptions table
    cursor.execute("PRAGMA table_info(prescriptions)")
    prescription_columns = [col[1] for col in cursor.fetchall()]

    if "file_path" not in prescription_columns:
        cursor.execute("ALTER TABLE prescriptions ADD COLUMN file_path TEXT")

    if "status" not in prescription_columns:
        cursor.execute("ALTER TABLE prescriptions ADD COLUMN status TEXT DEFAULT 'Pending'")

    if "uploaded_at" not in prescription_columns:
        cursor.execute("ALTER TABLE prescriptions ADD COLUMN uploaded_at DATETIME")

    conn.commit()
    conn.close()