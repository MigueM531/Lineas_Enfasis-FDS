class Docente:
    def __init__(self, id_docente, nombre):
        self.id_docente = id_docente
        self.nombre = nombre

    def registrar_cronograma(self, curso, cronograma):
        curso.cronograma = cronograma
        return f"Cronograma registrado en {curso.nombre}"

    def ingresar_notas(self, curso, notas):
        curso.notas = notas
        return f"Notas ingresadas en {curso.nombre}"