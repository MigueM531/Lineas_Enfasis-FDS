class Reporte:
    def __init__(self, id: int, estudiante_id: int, tipo: str, contenido: list = None):
        self.id = id
        self.estudiante_id = estudiante_id
        self.tipo = tipo
        self.contenido = contenido if contenido else []

    def generar(self):
        print("Generando reporte...")

    def exportar(self):
        print("Exportando reporte...")
