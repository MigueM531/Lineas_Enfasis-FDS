class ChatBot:
    def __init__(self, nombre="EduBot"):
        self.nombre = nombre

    def mostrar_cursos(self, cursos):
        return [f"{c.codigo} - {c.nombre} ({c.estado})" for c in cursos]

    def validar_inscripciones(self, estudiante, curso, cumple_prerrequisitos, cupo_disponible):
        return estudiante.inscribirse(curso, cumple_prerrequisitos, cupo_disponible)

    def generar_reportes(self, estudiante):
        return estudiante.pedir_reporte()

    def notificar(self, estudiante, mensaje):
        return estudiante.recibir_notificacion(mensaje)