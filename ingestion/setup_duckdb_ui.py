import duckdb, uuid, json, datetime as dt
from pathlib import Path
import time
print("DuckDB setup script started...")
# -------------------------------------------------
# 0) parameters
# -------------------------------------------------
JSON_PATH     = '.duckdb/ntb_exploration.json'
ts               = dt.datetime.now()
notebook_name    = f"medical-analysis-{ts.isoformat(timespec='seconds')}"
notebook_id      = uuid.uuid4()

# -------------------------------------------------
# 1) connection (pure RAM, no ui.db created on disk)
# -------------------------------------------------
print("Connecting to DuckDB in-memory database...")
con = duckdb.connect(database=':memory:')

con.execute("INSTALL 'ui'")
con.execute("LOAD 'ui'")
con.execute("CALL start_ui_server();")   # creates/attaches the real ui.db

print("😴 Sleeping for 5 seconds to ensure the UI server is ready...")
time.sleep(5)
print("⌚Sleep finished, proceeding with setup...")

for attempt in range(1, 4):                           # 3 shots
    try:
        already_there = (
            con.execute(f"""
                SELECT 1
                FROM   _duckdb_ui.notebook_versions
                WHERE  title LIKE '%{notebook_name}%'
                  AND  expires IS NULL
                LIMIT  1
            """).fetchone() is not None
        )
        break                                         # success
    except Exception as e:
        print(f"attempt {attempt} out of 3 failed, retrying in 5 s → {e}")
        if attempt == 3:                              # last try—give up
            raise
        time.sleep(5)                                # wait 5 s, then retry
created = False

# -------------------------------------------------
# 4) insert only when necessary
# -------------------------------------------------
if not already_there:
    

    con.execute(f"set variable notebook_content = (select json from '{JSON_PATH}')")
    con.execute("BEGIN TRANSACTION")

    con.execute("""
        INSERT INTO _duckdb_ui.notebooks (id, name, created)
        VALUES (?, ?, ?)
    """, (notebook_id, f"notebook_{notebook_id}", ts))

    con.execute("""
        INSERT INTO _duckdb_ui.notebook_versions
               (notebook_id, version, title, json, created, expires)
        VALUES (?, 1, ?, getvariable('notebook_content'), ?, NULL)
    """, (
        notebook_id,
        notebook_name,
        ts,
    ))

    con.execute("COMMIT")
    created = True
    print(notebook_name, " loaded from ", JSON_PATH, " into ", notebook_id, " at ", ts)

con.close()  # close the connection to the in-memory database

# -------------------------------------------------
# 5) outcome
# -------------------------------------------------
if created: print("✅  Notebook imported.")
else: print("ℹ️  Notebook already present — nothing done.")
