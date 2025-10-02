from datetime import date

class Inscripcion:
    def __init__(self, id: int, estudiante_id: int, curso_id: int, fecha_inscripcion: date, estado: str):
        self.id = id
        self.estudiante_id = estudiante_id
        self.curso_id = curso_id
        self.fecha_inscripcion = fecha_inscripcion
        self.estado = estado

    def validar_prerrequisitos(self):
        print("Validando prerrequisitos...")

    def registrar(self):
        print("Inscripción registrada")
