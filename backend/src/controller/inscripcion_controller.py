import sys
from fastapi import APIRouter
from database import get_connection
from model.Inscripcion import Inscripcion

sys.path.append("src")

router = APIRouter(prefix="/inscripciones", tags=["Inscripciones"])


class InscripcionController:

    def crear_inscripcion(self, estudiante_id: int, curso_id: int):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO inscripciones (estudiante_id, curso_id)
            VALUES (%s, %s)
            RETURNING id, fecha_inscripcion, estado
        """, (estudiante_id, curso_id))
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return Inscripcion(row[0], estudiante_id, curso_id, row[1], row[2])

    def listar_inscripciones(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, estudiante_id, curso_id, fecha_inscripcion, estado FROM inscripciones")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Inscripcion(*row) for row in rows]


# -------- Rutas API usando el controlador -------- #
controller = InscripcionController()

@router.post("/")
def crear_inscripcion(estudiante_id: int, curso_id: int):
    return controller.crear_inscripcion(estudiante_id, curso_id).__dict__

@router.get("/")
def listar_inscripciones():
    return [i.__dict__ for i in controller.listar_inscripciones()]

