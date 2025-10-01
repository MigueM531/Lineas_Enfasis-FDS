from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Importar tus controladores existentes
from controller.curso_controller import CursoController
from controller.estudiante_controller import EstudianteController
from controller.coordinador_controller import CoordinadorController
from model.Estudiante import Estudiante
from model.Coordinador import Coordinador

# Inicializar FastAPI
app = FastAPI(title="EduBot API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: ["http://localhost:3000", "https://tu-dominio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciar controladores
curso_ctrl = CursoController()
estudiante_ctrl = EstudianteController()
coordinador_ctrl = CoordinadorController()


# ==================== MODELOS PYDANTIC ====================

class Message(BaseModel):
    text: str
    estudiante_id: int = 1


class InscripcionRequest(BaseModel):
    estudiante_id: int
    curso_codigo: str


class CursoCreate(BaseModel):
    codigo: str
    nombre: str
    cupo: int
    semestre: int
    id_docente: Optional[int] = None


class CursoAprobar(BaseModel):
    codigo: str
    coordinador_id: int = 1


# ==================== ENDPOINTS ====================

@app.get("/")
def read_root():
    return {
        "message": "EduBot API - Sistema de Líneas de Énfasis",
        "status": "active",
        "version": "1.0.0"
    }


# HU1 & HU2: Consultar y filtrar cursos
@app.get("/api/cursos")
def listar_cursos(semestre: Optional[int] = None, estado: Optional[str] = None):
    try:
        cursos = curso_ctrl.listar_cursos()

        # Filtrar por semestre si se proporciona
        if semestre:
            cursos = [c for c in cursos if c.semestre == semestre]

        # Filtrar por estado si se proporciona (por defecto solo aprobados)
        if estado:
            cursos = [c for c in cursos if c.estado == estado]
        else:
            cursos = [c for c in cursos if c.estado == "aprobado"]

        # Convertir objetos Curso a diccionarios
        cursos_dict = [
            {
                "codigo": c.codigo,
                "nombre": c.nombre,
                "cupo": c.cupo,
                "semestre": c.semestre,
                "estado": c.estado
            }
            for c in cursos
        ]

        return {
            "type": "cursos",
            "data": cursos_dict,
            "count": len(cursos_dict)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HU1: Obtener detalle de un curso específico
@app.get("/api/cursos/{codigo}")
def obtener_curso(codigo: str):
    try:
        cursos = curso_ctrl.listar_cursos()
        curso = next((c for c in cursos if c.codigo == codigo), None)

        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        # Obtener número de inscritos
        inscritos = curso_ctrl.contar_inscritos(codigo)

        return {
            "codigo": curso.codigo,
            "nombre": curso.nombre,
            "cupo": curso.cupo,
            "semestre": curso.semestre,
            "estado": curso.estado,
            "inscritos": inscritos,
            "cupos_disponibles": curso.cupo - inscritos
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HU3: Validar cupos y prerequisitos antes de inscripción
@app.get("/api/cursos/{codigo}/validar")
def validar_curso(codigo: str, estudiante_id: int):
    try:
        cursos = curso_ctrl.listar_cursos()
        curso = next((c for c in cursos if c.codigo == codigo), None)

        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        inscritos = curso_ctrl.contar_inscritos(codigo)
        cupos_disponibles = curso.validar_cupo(inscritos)

        validaciones = {
            "cupos_disponibles": cupos_disponibles,
            "estado_aprobado": curso.estado == "aprobado",
            "puede_inscribirse": cupos_disponibles and curso.estado == "aprobado",
            "mensaje": []
        }

        if not cupos_disponibles:
            validaciones['mensaje'].append("No hay cupos disponibles")

        if curso.estado != "aprobado":
            validaciones['mensaje'].append("El curso no está aprobado para inscripciones")

        return validaciones

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HU5: Inscribirse en un curso
@app.post("/api/inscripciones")
def inscribir_estudiante(inscripcion: InscripcionRequest):
    try:
        # Obtener el curso
        cursos = curso_ctrl.listar_cursos()
        curso = next((c for c in cursos if c.codigo == inscripcion.curso_codigo), None)

        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        # Crear objeto estudiante (en producción obtenerlo de la BD)
        estudiante = Estudiante(
            inscripcion.estudiante_id,
            "Estudiante",  # Deberías obtener el nombre real de la BD
            "Programa"  # Deberías obtener el programa real de la BD
        )

        # Validar cupos
        inscritos = curso_ctrl.contar_inscritos(curso.codigo)
        tiene_cupo = curso.validar_cupo(inscritos)

        # Intentar inscripción usando tu lógica existente
        resultado = estudiante_ctrl.inscribir(estudiante, curso, True, tiene_cupo)

        if "éxito" in resultado.lower() or "inscripción realizada" in resultado.lower():
            return {
                "type": "inscripcion",
                "resultado": resultado,
                "success": True
            }
        else:
            return {
                "type": "inscripcion",
                "resultado": resultado,
                "success": False
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HU2: Mis inscripciones
@app.get("/api/estudiante/{estudiante_id}/inscripciones")
def obtener_inscripciones(estudiante_id: int):
    try:
        # Aquí debes implementar la lógica para obtener inscripciones
        # desde tu base de datos usando tus controladores

        # Por ahora retorno ejemplo
        return {
            "type": "inscripciones",
            "data": [],
            "count": 0,
            "message": "Consulta tus inscripciones desde la base de datos"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HU7: Reporte de progreso
@app.get("/api/estudiante/{estudiante_id}/progreso")
def obtener_progreso(estudiante_id: int):
    try:
        # Datos simulados - implementar lógica real con tus controladores
        return {
            "type": "reporte",
            "data": {
                "creditos_completados": 24,
                "creditos_totales": 36,
                "promedio": 4.2,
                "pendientes": 4
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HU9: Crear curso (coordinador)
@app.post("/api/cursos")
def crear_curso(curso: CursoCreate):
    try:
        nuevo_curso = curso_ctrl.crear_curso(
            curso.codigo,
            curso.nombre,
            curso.cupo,
            curso.semestre
        )

        return {
            "type": "curso_creado",
            "mensaje": f"Curso {nuevo_curso.codigo} creado exitosamente. Estado: {nuevo_curso.estado}",
            "codigo": nuevo_curso.codigo,
            "data": {
                "codigo": nuevo_curso.codigo,
                "nombre": nuevo_curso.nombre,
                "cupo": nuevo_curso.cupo,
                "semestre": nuevo_curso.semestre,
                "estado": nuevo_curso.estado
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HU4: Aprobar curso (coordinador)
@app.put("/api/cursos/{codigo}/aprobar")
def aprobar_curso(codigo: str, coordinador_id: int = 1):
    try:
        # Obtener curso
        cursos = curso_ctrl.listar_cursos()
        curso = next((c for c in cursos if c.codigo == codigo), None)

        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        # Crear objeto coordinador
        coordinador = Coordinador(coordinador_id, "Dr. Coordinador")

        # Aprobar usando tu lógica existente
        resultado = coordinador_ctrl.aprobar_curso(curso)

        return {
            "type": "curso_aprobado",
            "mensaje": resultado,
            "codigo": codigo
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HU4: Rechazar curso (coordinador)
@app.put("/api/cursos/{codigo}/rechazar")
def rechazar_curso(codigo: str, coordinador_id: int = 1):
    try:
        cursos = curso_ctrl.listar_cursos()
        curso = next((c for c in cursos if c.codigo == codigo), None)

        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        coordinador = Coordinador(coordinador_id, "Dr. Coordinador")
        resultado = coordinador_ctrl.rechazar_curso(curso)

        return {
            "type": "curso_rechazado",
            "mensaje": resultado,
            "codigo": codigo
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint principal del chat
@app.post("/chat")
def chat(message: Message):
    try:
        text = message.text.lower()

        # Buscar cursos
        if "buscar" in text or "curso" in text or "disponible" in text:
            return listar_cursos(estado="aprobado")

        # Inscribirse
        elif "inscrib" in text:
            # Extraer código del curso
            palabras = message.text.split()
            codigo = None
            for palabra in palabras:
                if len(palabra) >= 3:
                    codigo = palabra.upper()
                    break

            if codigo:
                inscripcion = InscripcionRequest(
                    estudiante_id=message.estudiante_id,
                    curso_codigo=codigo
                )
                return inscribir_estudiante(inscripcion)

            return {"type": "error", "message": "Por favor especifica el código del curso"}

        # Progreso
        elif "reporte" in text or "progreso" in text:
            return obtener_progreso(message.estudiante_id)

        # Mis inscripciones
        elif "mis inscripc" in text or "inscripciones" in text:
            return obtener_inscripciones(message.estudiante_id)

        # Filtrar por semestre
        elif "semestre" in text or "filtrar" in text:
            # Intentar extraer número de semestre
            import re
            numeros = re.findall(r'\d+', text)
            if numeros:
                semestre = int(numeros[0])
                return listar_cursos(semestre=semestre, estado="aprobado")
            return listar_cursos(estado="aprobado")

        # Respuesta por defecto
        return {
            "type": "default",
            "message": "No entendí tu consulta. Intenta con: 'buscar cursos', 'inscribirme en [CODIGO]', 'mi progreso', o 'mis inscripciones'"
        }

    except Exception as e:
        return {
            "type": "error",
            "message": f"Error procesando mensaje: {str(e)}"
        }


# Ejecutar con: uvicorn api:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)