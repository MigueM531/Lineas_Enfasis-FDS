class LineaEnfasis:
    def __init__(self, id_linea: int, nombre: str, cursos: list = None):
        self.id_linea = id_linea
        self.nombre = nombre
        self.cursos = cursos if cursos else []

    def consultar_cursos(self):
        print("Consultando cursos de la línea de énfasis")
        return self.cursos

    def filtrar_semestre(self, semestre: str):
        print(f"Filtrando cursos por semestre {semestre}")
