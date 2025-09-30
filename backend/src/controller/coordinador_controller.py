from database import get_connection

class CoordinadorController:
    def aprobar_curso(self, curso):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE cursos SET estado = 'aprobado' WHERE codigo = %s", (curso.codigo,))
        conn.commit()
        cur.close()
        conn.close()
        return f"Curso {curso.codigo} aprobado en BD"
