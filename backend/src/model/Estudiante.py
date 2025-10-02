class Estudiante:
    def __init__(self, id: int, nombre: str, contrasena: str, programa: str, creditos_aprob: int, cursos: list = None):
        self.id = id
        self.nombre = nombre
        self.contrasena = contrasena
        self.programa = programa
        self.creditos_aprob = creditos_aprob
        self.cursos = cursos if cursos else []

    def consultar_cursos(self):
        print("Consultando cursos...")
        return self.cursos

    def inscribirse(self, curso):
        print(f"{self.nombre} se inscribió en {curso}")
        self.cursos.append(curso)

    def cancelar_curso(self, curso):
        if curso in self.cursos:
            print(f"{self.nombre} canceló el curso {curso}")
            self.cursos.remove(curso)
