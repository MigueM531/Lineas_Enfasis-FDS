class Admin:
    def __init__(self, id: int, nombre: str, contrasena: str):
        self.id = id
        self.nombre = nombre
        self.contrasena = contrasena

    def consultar_auditoria(self):
        print("Consultando auditoría...")

    def gestionar_usuarios(self):
        print("Gestionando usuarios...")
