import re
from controller.inscripcion_controller import InscripcionController

class ChatBot:
    def __init__(self):
        self.inscripcion_controller = InscripcionController()

    def procesar_mensaje(self, mensaje: str, estudiante_id: int = 1):
        mensaje = mensaje.lower()

        # Detectar intención de inscripción
        match = re.search(r"(inscribirme|inscribir|registrarme).*(curso\s*(\d+))", mensaje)
        if match:
            curso_id = int(match.group(3))
            inscripcion = self.inscripcion_controller.crear_inscripcion(estudiante_id, curso_id)
            return f"✅ Te inscribí en el curso {curso_id}. Estado: {inscripcion.estado}"

        # Si no reconoce el mensaje
        return "🤖 No entendí tu mensaje, ¿quieres inscribirte en un curso?"
