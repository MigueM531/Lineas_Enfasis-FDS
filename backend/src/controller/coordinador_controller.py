import sys
sys.path.append("src")

from database import get_connection
from model.Coordinador import Coordinador

class CoordinadorController:
    def crear_coordinador(self, nombre):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO coordinadores (nombre)
            VALUES (%s)
            RETURNING id_coordinador
        """, (nombre,))
        id_coordinador = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return Coordinador(id_coordinador, nombre)

    def listar_coordinadores(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_coordinador, nombre FROM coordinadores")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Coordinador(*row) for row in rows]

