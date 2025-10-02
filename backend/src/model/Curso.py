class Curso:
    def __init__(self, id_curso: int, nombre: str, cupo: int, creditos: int, cronograma: list = None, estado: str = "pendiente"):
        self.id_curso = id_curso
        self.nombre = nombre
        self.cupo = cupo
        self.creditos = creditos
        self.cronograma = cronograma if cronograma else []
        self.estado = estado

    def validar_cupo(self):
        return self.cupo > 0
