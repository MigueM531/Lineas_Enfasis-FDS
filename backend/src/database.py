import psycopg2
import os

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("PGDATABASE", "neondb"),
        user=os.getenv("PGUSER", "neondb_owner"),
        password=os.getenv("PGPASSWORD", "npg_RJbZgCY5i1Xq"),
        host=os.getenv("PGHOST", "ep-shy-queen-adgkvidp-pooler.c-2.us-east-1.aws.neon.tech"),
        port=5432,
        sslmode=os.getenv("PGSSLMODE", "require"),
        channel_binding=os.getenv("PGCHANNELBINDING", "require")
    )


def init_db():
    """Verifica si existen tablas y, si no, ejecuta schema.sql."""
    conn = get_connection()
    cur = conn.cursor()

    # Verificar si existe la tabla cursos
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'cursos'
        );
    """)
    exists = cur.fetchone()[0]

    if not exists:
        print("⚠️ Tablas no encontradas. Ejecutando schema.sql...")
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            sql_script = f.read()
            cur.execute(sql_script)
        conn.commit()
        print("✅ Tablas creadas correctamente.")
    else:
        print("✅ Tablas ya existen, no es necesario recrearlas.")

    cur.close()
    conn.close()