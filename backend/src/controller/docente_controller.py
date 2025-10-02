import sys
sys.path.append("src")

from database import get_connection
from model.Docente import Docente

class DocenteController:
    def crear_docente(self, nombre):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO docentes (nombre)
            VALUES (%s)
            RETURNING id_docente
        """, (nombre,))
        id_docente = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return Docente(id_docente, nombre)

    def listar_docentes(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_docente, nombre FROM docentes")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Docente(*row) for row in rows]
