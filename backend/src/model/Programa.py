class Programa:
    def __init__(self, id_programa: int, nombre: str, lineas_enfasis: list = None):
        self.id_programa = id_programa
        self.nombre = nombre
        self.lineas_enfasis = lineas_enfasis if lineas_enfasis else []
