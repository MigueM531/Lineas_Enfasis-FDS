from backend.src.database import get_connection

class EstudianteController:
    def inscribir(self, estudiante, curso, cumple_prerrequisitos, cupo_disponible):
        resultado = estudiante.inscribirse(curso, cumple_prerrequisitos, cupo_disponible)
        if resultado == "Inscripción exitosa":
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO inscripciones (estudiante_id, curso_codigo)
                VALUES (%s, %s)
            """, (estudiante.id_estudiante, curso.codigo))
            conn.commit()
            cur.close()
            conn.close()
        return resultado