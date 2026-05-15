#!/usr/bin/env python3
"""
Migrate data from the local SQLite file (kids_ecommerce.db) to MySQL (XAMPP).

Usage (PowerShell):
  # 1) Ensure MySQL is running in XAMPP and a database exists (kids_ecommerce)
  # 2) Set connection (you can also edit .env and skip env vars)
  $env:DATABASE_URI = "mysql+pymysql://root@127.0.0.1:3306/kids_ecommerce?charset=utf8mb4"
  # 3) Run migration
  python scripts/migrate_sqlite_to_mysql.py

Notes
- The script creates any missing tables in MySQL using your current models (app.py),
  then copies rows from SQLite into the matching tables/columns.
- Only columns that exist in both source and target are copied.
- Foreign key checks are disabled temporarily during copy to avoid ordering issues.
- Keep a backup of kids_ecommerce.db before running, just in case.
"""
import os
import json
from typing import List
from sqlalchemy import create_engine, text, inspect, Table, MetaData, select
from sqlalchemy.engine import make_url

# Paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys as _sys
if PROJECT_DIR not in _sys.path:
    _sys.path.insert(0, PROJECT_DIR)
# Allow override via env var SQLITE_PATH; otherwise try common locations
ENV_SQLITE = os.getenv("SQLITE_PATH")
CANDIDATE_SQLITES = [
    ENV_SQLITE,
    os.path.join(PROJECT_DIR, "kids_ecommerce.db"),
    os.path.join(PROJECT_DIR, "instance", "kids_ecommerce.db"),
]
SQLITE_PATH = next((p for p in CANDIDATE_SQLITES if p and os.path.exists(p)), None)


def _mysql_url_from_env() -> str:
    url = os.getenv("DATABASE_URI")
    if url:
        return url
    user = os.getenv("MYSQL_USER", "root")
    pwd = os.getenv("MYSQL_PASSWORD", "")
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    db = os.getenv("MYSQL_DB", "kids_ecommerce")
    auth = f"{user}:{pwd}@" if pwd else f"{user}@"
    return f"mysql+pymysql://{auth}{host}:{port}/{db}?charset=utf8mb4"


def _list_tables_sqlite(engine) -> List[str]:
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"))
        return [r[0] for r in rows]


def _list_tables_mysql(engine) -> List[str]:
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()"))
        return [r[0] for r in rows]


def _quote_mysql(name: str) -> str:
    return f"`{name}`"


def _ensure_mysql_database(mysql_url: str):
    url = make_url(mysql_url)
    dbname = url.database
    if not dbname:
        return
    server_url = url.set(database=None)
    engine = create_engine(server_url, pool_pre_ping=True)
    stmt = text(
        f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def main():
    if not SQLITE_PATH:
        tried = [p for p in CANDIDATE_SQLITES if p]
        msg = "SQLite file not found. Tried: " + ", ".join(tried)
        raise SystemExit(msg)

    mysql_url = _mysql_url_from_env()
    print(f"Using MySQL URL: {mysql_url}")

    # Ensure target database exists
    try:
        _ensure_mysql_database(mysql_url)
    except Exception as e:
        print(f"[warn] Failed to ensure database exists: {e}")

    # Engines
    sqlite_engine = create_engine(f"sqlite:///{SQLITE_PATH}")
    mysql_engine = create_engine(mysql_url, pool_pre_ping=True)

    # Ensure target schema exists from models
    print("Creating tables in MySQL from models (if missing)...")
    os.environ["DATABASE_URI"] = mysql_url  # ensure app loads MySQL
    from app import app, db  # import after env is set
    with app.app_context():
        db.create_all()

    src_tables = _list_tables_sqlite(sqlite_engine)
    dst_tables = _list_tables_mysql(mysql_engine)
    common = set(src_tables) & set(dst_tables)
    if not common:
        print("No common tables to migrate. Exiting.")
        return

    # Recommended order to reduce FK issues; rest appended later
    preferred_order = [
        "user", "category", "subcategory", "product", "address",
        "seller_application", "order", "order_item", "order_label",
        "review", "notification", "wishlist", "cart",
        "wallet_transaction", "rider_application", "return_request",
        "return_pickup", "qr_scan_log", "product_qr",
        "oauth", "flask_dance_oauth", "follow", "store_chat_message",
        "theme_setting", "admin_profile", "admin_security_log"
    ]
    ordered = [t for t in preferred_order if t in common]
    ordered += [t for t in sorted(common) if t not in ordered]

    src_inspector = inspect(sqlite_engine)
    dst_inspector = inspect(mysql_engine)

    with sqlite_engine.begin() as src_conn, mysql_engine.begin() as dst_conn:
        # disable FKs during bulk copy
        try:
            src_conn.execute(text("PRAGMA foreign_keys=OFF"))
        except Exception:
            pass
        try:
            dst_conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        except Exception:
            pass

        mode = os.getenv("MIGRATE_MODE", "merge").lower()  # 'merge' or 'clean'
        if mode not in ("merge", "clean"):
            mode = "merge"
        if mode == "clean":
            # truncate destination tables first
            for t in ordered[::-1]:
                try:
                    dst_conn.execute(text(f"TRUNCATE TABLE {_quote_mysql(t)}"))
                except Exception:
                    pass
            print("[info] Destination tables truncated (clean mode)")

        for table in ordered:
            try:
                src_cols = {c['name'] for c in src_inspector.get_columns(table)}
                dst_cols = {c['name'] for c in dst_inspector.get_columns(table)}
            except Exception:
                print(f"[skip] Could not inspect table: {table}")
                continue
            cols = [c for c in dst_cols if c in src_cols]
            if not cols:
                print(f"[skip] No overlapping columns for {table}")
                continue

            # reflect source table
            meta = MetaData()
            src_tbl = Table(table, meta, autoload_with=sqlite_engine)
            sel_cols = [src_tbl.c[c] for c in cols]
            rows = src_conn.execute(select(*sel_cols)).mappings().all()
            if not rows:
                print(f"[ok] {table}: nothing to copy")
                continue

            placeholders = ", ".join(f":{c}" for c in cols)
            cols_sql = ", ".join(_quote_mysql(c) for c in cols)

            if mode == "merge":
                update_pairs = ", ".join(f"{_quote_mysql(c)}=VALUES({_quote_mysql(c)})" for c in cols if c.lower() not in ("id",))
                sql = text(
                    f"INSERT INTO {_quote_mysql(table)} ({cols_sql}) VALUES ({placeholders}) "
                    f"ON DUPLICATE KEY UPDATE {update_pairs}"
                )
            else:
                sql = text(f"INSERT INTO {_quote_mysql(table)} ({cols_sql}) VALUES ({placeholders})")

            # normalize JSON-like values to native str for safety
            def _normalize(mapping):
                out = {}
                for k, v in mapping.items():
                    if isinstance(v, (dict, list)):
                        out[k] = json.dumps(v, ensure_ascii=False)
                    else:
                        out[k] = v
                return out

            data = [_normalize(dict(r)) for r in rows]
            dst_conn.execute(sql, data)
            print(f"[ok] {table}: copied {len(data)} row(s)")

        try:
            dst_conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        except Exception:
            pass

    print("Done. Review output above for any skips.")


if __name__ == "__main__":
    main()
