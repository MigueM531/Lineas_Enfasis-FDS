from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import re

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
        "version": "1.0.0",
        "endpoints": {
            "cursos": "/api/cursos",
            "crear_curso": "/api/cursos (POST)",
            "aprobar_curso": "/api/cursos/{codigo}/aprobar (PUT)",
            "rechazar_curso": "/api/cursos/{codigo}/rechazar (PUT)",
            "inscripciones": "/api/inscripciones (POST)",
            "chat": "/chat (POST)"
        }
    }


# HU1 & HU2: Consultar y filtrar cursos
@app.get("/api/cursos")
def listar_cursos(semestre: Optional[int] = None, estado: Optional[str] = None):
    """
    Lista cursos con filtros opcionales
    - semestre: filtra por número de semestre
    - estado: filtra por estado (aprobado, pendiente, rechazado)
    """
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
    """Obtiene los detalles completos de un curso específico"""
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
    """Valida si un estudiante puede inscribirse en un curso"""
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
    """Inscribe a un estudiante en un curso"""
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
    """Obtiene todas las inscripciones de un estudiante"""
    try:
        # Implementar lógica real con tus controladores
        # Por ahora retorno estructura básica
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
    """Genera reporte de progreso académico de un estudiante"""
    try:
        # Implementar lógica real con tus controladores
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
    """Crea un nuevo curso en el sistema (requiere rol coordinador)"""
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
    """Aprueba un curso pendiente (requiere rol coordinador)"""
    try:
        # Obtener curso
        cursos = curso_ctrl.listar_cursos()
        curso = next((c for c in cursos if c.codigo == codigo), None)

        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        # Validar que el curso esté pendiente
        if curso.estado != "pendiente":
            return {
                "type": "error",
                "mensaje": f"El curso ya tiene estado: {curso.estado}",
                "codigo": codigo
            }

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
    """Rechaza un curso pendiente (requiere rol coordinador)"""
    try:
        cursos = curso_ctrl.listar_cursos()
        curso = next((c for c in cursos if c.codigo == codigo), None)

        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        # Validar que el curso esté pendiente
        if curso.estado != "pendiente":
            return {
                "type": "error",
                "mensaje": f"El curso ya tiene estado: {curso.estado}",
                "codigo": codigo
            }

        coordinador = Coordinador(coordinador_id, "Dr. Coordinador")
        resultado = coordinador_ctrl.rechazar_curso(curso)

        return {
            "type": "curso_rechazado",
            "mensaje": resultado,
            "codigo": codigo
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HU6: Obtener notificaciones (NUEVO)
@app.get("/api/notificaciones/{usuario_id}")
def obtener_notificaciones(usuario_id: int):
    """Obtiene las notificaciones de un usuario"""
    try:
        # Simulación de notificaciones - implementar lógica real
        notificaciones = [
            {
                "tipo": "cambio_horario",
                "curso": "Machine Learning Avanzado",
                "mensaje": "El horario cambió a Miércoles 6:00-9:00 PM",
                "fecha": "Hace 2 horas",
                "leido": False
            },
            {
                "tipo": "cupos",
                "curso": "Deep Learning Aplicado",
                "mensaje": "¡Nuevos cupos disponibles!",
                "fecha": "Hace 1 día",
                "leido": False
            }
        ]

        return {
            "type": "notificaciones",
            "data": notificaciones,
            "count": len(notificaciones)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HU8: Generar comprobante (NUEVO)
@app.post("/api/comprobante/generar")
def generar_comprobante(inscripcion: InscripcionRequest):
    """Genera un comprobante de inscripción"""
    try:
        import random

        return {
            "type": "comprobante",
            "mensaje": "Comprobante generado exitosamente",
            "data": {
                "numero_transaccion": f"#{random.randint(100000, 999999)}",
                "estudiante_id": inscripcion.estudiante_id,
                "curso_codigo": inscripcion.curso_codigo,
                "fecha": datetime.now().isoformat(),
                "estado": "Pagado"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint de estadísticas para coordinadores (NUEVO)
@app.get("/api/estadisticas")
def obtener_estadisticas():
    """Obtiene estadísticas generales del sistema (coordinadores)"""
    try:
        cursos = curso_ctrl.listar_cursos()

        total_cursos = len(cursos)
        cursos_aprobados = len([c for c in cursos if c.estado == "aprobado"])
        cursos_pendientes = len([c for c in cursos if c.estado == "pendiente"])
        cursos_rechazados = len([c for c in cursos if c.estado == "rechazado"])

        # Calcular inscripciones totales
        total_inscripciones = sum([curso_ctrl.contar_inscritos(c.codigo) for c in cursos])

        return {
            "type": "estadisticas",
            "data": {
                "total_cursos": total_cursos,
                "cursos_aprobados": cursos_aprobados,
                "cursos_pendientes": cursos_pendientes,
                "cursos_rechazados": cursos_rechazados,
                "total_inscripciones": total_inscripciones,
                "ocupacion_promedio": "75%"  # Calcular real
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint principal del chat (MEJORADO)
@app.post("/chat")
def chat(message: Message):
    """
    Endpoint principal del chatbot
    Procesa mensajes en lenguaje natural y retorna respuestas apropiadas
    """
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
                    # Buscar código que coincida con patrón de curso
                    codigo_upper = palabra.upper()
                    cursos = curso_ctrl.listar_cursos()
                    if any(c.codigo == codigo_upper for c in cursos):
                        codigo = codigo_upper
                        break

            if codigo:
                inscripcion = InscripcionRequest(
                    estudiante_id=message.estudiante_id,
                    curso_codigo=codigo
                )
                return inscribir_estudiante(inscripcion)

            return {
                "type": "error",
                "message": "Por favor especifica el código del curso. Ejemplo: 'inscribirme en IA-501'"
            }

        # Progreso
        elif "reporte" in text or "progreso" in text:
            return obtener_progreso(message.estudiante_id)

        # Mis inscripciones
        elif "mis inscripc" in text or "inscripciones" in text:
            return obtener_inscripciones(message.estudiante_id)

        # Notificaciones
        elif "notificacion" in text or "aviso" in text:
            return obtener_notificaciones(message.estudiante_id)

        # Filtrar por semestre
        elif "semestre" in text or "filtrar" in text:
            # Intentar extraer número de semestre
            numeros = re.findall(r'\d+', text)
            if numeros:
                semestre = int(numeros[0])
                return listar_cursos(semestre=semestre, estado="aprobado")
            return listar_cursos(estado="aprobado")

        # Crear curso (coordinador)
        elif "crear curso" in text:
            return {
                "type": "info",
                "message": "Para crear un curso, usa el formulario en la interfaz o envía una petición POST a /api/cursos"
            }

        # Aprobar cursos (coordinador)
        elif "aprobar" in text or "pendiente" in text:
            return listar_cursos(estado="pendiente")

        # Estadísticas (coordinador)
        elif "estadistica" in text or "reporte" in text:
            return obtener_estadisticas()

        # Respuesta por defecto
        return {
            "type": "default",
            "message": "No entendí tu consulta. Intenta con:\n" +
                       "• 'buscar cursos'\n" +
                       "• 'inscribirme en [CODIGO]'\n" +
                       "• 'mi progreso'\n" +
                       "• 'mis inscripciones'\n" +
                       "• 'filtrar por semestre [NUMERO]'\n" +
                       "• 'notificaciones'"
        }

    except Exception as e:
        return {
            "type": "error",
            "message": f"Error procesando mensaje: {str(e)}"
        }


# Health check endpoint
@app.get("/health")
def health_check():
    """Verifica el estado de la API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# Ejecutar con: uvicorn api:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)