import sys
sys.path.append("src")

from database import get_connection
from model.Inscripcion import Inscripcion

class InscripcionController:
    def crear_inscripcion(self, estudiante_id, curso_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO inscripciones (estudiante_id, curso_id)
            VALUES (%s, %s)
            RETURNING id, fecha_inscripcion
        """, (estudiante_id, curso_id))
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return Inscripcion(row[0], estudiante_id, curso_id, row[1])

    def listar_inscripciones(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, estudiante_id, curso_id, fecha_inscripcion FROM inscripciones")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Inscripcion(*row) for row in rows]
