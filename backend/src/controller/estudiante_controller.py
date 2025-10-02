import sys
sys.path.append("src")

from database import get_connection
from model.Estudiante import Estudiante

class EstudianteController:
    def crear_estudiante(self, nombre, programa, rol="estudiante"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO estudiantes (nombre, programa, rol)
            VALUES (%s, %s, %s)
            RETURNING id_estudiante
        """, (nombre, programa, rol))
        id_estudiante = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return Estudiante(id_estudiante, nombre, programa, rol)

    def listar_estudiantes(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_estudiante, nombre, programa, rol FROM estudiantes")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Estudiante(*row) for row in rows]
