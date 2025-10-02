class Notificacion:
    def __init__(self, id: int, estudiante_id: int, mensaje: str, leido: bool = False):
        self.id = id
        self.estudiante_id = estudiante_id
        self.mensaje = mensaje
        self.leido = leido

    def enviar(self):
        print(f"Enviando notificación: {self.mensaje}")

    def marcar_como_leida(self):
        self.leido = True
        print("Notificación marcada como leída")
