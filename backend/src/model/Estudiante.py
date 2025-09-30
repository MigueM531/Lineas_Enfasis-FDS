class Estudiante:
    def __init__(self, id_estudiante, nombre, programa):
        self.id_estudiante = id_estudiante
        self.nombre = nombre
        self.programa = programa

    def consultar_cursos(self):
        pass

    def inscribirse(self, curso, cumple_prerrequisitos, cupo_disponible):
        if not cumple_prerrequisitos:
            return "No cumple prerrequisitos"
        if not cupo_disponible:
            return "Cupo lleno"
        return "Inscripción exitosa"

    def recibir_notificacion(self, mensaje):
        return f"Notificación para {self.nombre}: {mensaje}"

    def pedir_reporte(self):
        return f"Reporte académico solicitado por {self.nombre}"