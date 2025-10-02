import sys
sys.path.append("src")

from database import get_connection
from model.Curso import Curso

class CursoController:
    def crear_curso(self, nombre, cupo, creditos, cronograma):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO cursos (nombre, cupo, creditos, cronograma, estado)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING idCurso, estado
        """, (nombre, cupo, creditos, cronograma, "pendiente"))
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return Curso(row[0], nombre, cupo, creditos, cronograma, row[1])

    def listar_cursos(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT idCurso, nombre, cupo, creditos, cronograma, estado FROM cursos")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Curso(*row) for row in rows]

    def contar_inscritos(self, curso_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM inscripciones WHERE curso_id = %s", (curso_id,))
        inscritos = cur.fetchone()[0]
        cur.close()
        conn.close()
        return inscritos

