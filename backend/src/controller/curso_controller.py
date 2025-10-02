import sys
sys.path.append("src")

from database import get_connection
from model.Curso import Curso
import json

class CursoController:
    def crear_curso(self, nombre, cupo, creditos, cronograma=None, estado="pendiente"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO cursos (nombre, cupo, creditos, cronograma, estado)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_curso
        """, (nombre, cupo, creditos, json.dumps(cronograma if cronograma else []), estado))
        id_curso = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return Curso(id_curso, nombre, cupo, creditos, cronograma, estado)

    def listar_cursos(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_curso, nombre, cupo, creditos, cronograma, estado FROM cursos")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [Curso(row[0], row[1], row[2], row[3], row[4], row[5]) for row in rows]

    def contar_inscritos(self, id_curso):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM inscripciones WHERE curso_codigo = %s", (id_curso,))
        inscritos = cur.fetchone()[0]
        cur.close()
        conn.close()
        return inscritos

