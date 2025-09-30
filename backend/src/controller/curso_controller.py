import sys
sys.path.append("src")

from database import get_connection
from model.Curso import Curso

class CursoController:
    def crear_curso(self, codigo, nombre, cupo, semestre):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO cursos (codigo, nombre, cupo, semestre, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (codigo, nombre, cupo, semestre, "pendiente"))
        conn.commit()
        cur.close()
        conn.close()
        return Curso(codigo, nombre, cupo, semestre)

    def listar_cursos(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT codigo, nombre, cupo, semestre, estado FROM cursos")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Curso(*row) for row in rows]

    def contar_inscritos(self, codigo):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM inscripciones WHERE curso_codigo = %s", (codigo,))
        inscritos = cur.fetchone()[0]
        cur.close()
        conn.close()
        return inscritos