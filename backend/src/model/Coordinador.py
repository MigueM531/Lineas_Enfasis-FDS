class Coordinador:
    def __init__(self, id: int, nombre: str, contrasena: str):
        self.id = id
        self.nombre = nombre
        self.contrasena = contrasena

    def aprobar_curso(self, curso):
        print(f"Curso {curso} aprobado por {self.nombre}")

    def modificar_curso(self, curso):
        print(f"Curso {curso} modificado")

    def generar_reporte(self):
        print("Generando reporte...")

    def crear_curso(self, curso):
        print(f"Curso {curso} creado")

