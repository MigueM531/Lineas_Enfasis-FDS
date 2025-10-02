class Docente:
    def __init__(self, id: int, nombre: str, contrasena: str):
        self.id = id
        self.nombre = nombre
        self.contrasena = contrasena

    def registrar_notas(self, curso):
        print(f"Notas registradas en {curso}")

    def crear_cronograma(self, curso):
        print(f"Cronograma creado para {curso}")

    def subir_material(self, curso):
        print(f"Material subido para {curso}")
