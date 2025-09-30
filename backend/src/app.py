from fastapi import FastAPI
from pydantic import BaseModel
from controller.curso_controller import CursoController
from controller.estudiante_controller import EstudianteController
from model.Estudiante import Estudiante

app = FastAPI()
curso_ctrl = CursoController()
estudiante_ctrl = EstudianteController()

class Message(BaseModel):
    text: str
    estudiante_id: int = 1  # por ahora fijo

@app.post("/chat")
def chat(message: Message):
    text = message.text.lower()

    if "buscar" in text or "curso" in text:
        cursos = curso_ctrl.listar_cursos()
        return {
            "type": "cursos",
            "data": [
                {
                    "codigo": c.codigo,
                    "nombre": c.nombre,
                    "cupo": c.cupo,
                    "semestre": c.semestre,
                    "estado": c.estado,
                }
                for c in cursos if c.estado == "aprobado"
            ]
        }

    elif "inscribir" in text:
        # ejemplo: inscribir en MAT101
        codigo = "MAT101"
        cursos = curso_ctrl.listar_cursos()
        curso = next((c for c in cursos if c.codigo == codigo), None)
        if curso:
            estudiante = Estudiante(1, "Ana López", "Ingeniería")
            inscritos = curso_ctrl.contar_inscritos(curso.codigo)
            resultado = estudiante_ctrl.inscribir(estudiante, curso, True, curso.validar_cupo(inscritos))
            return {"type": "inscripcion", "resultado": resultado}
        return {"type": "error", "message": "Curso no encontrado"}

    elif "reporte" in text or "progreso" in text:
        return {
            "type": "reporte",
            "data": {
                "creditos_completados": 24,
                "creditos_totales": 36,
                "promedio": 4.2,
                "pendientes": 4
            }
        }

    return {"type": "default", "message": "No entendí, intenta con buscar cursos o inscribirme"}
