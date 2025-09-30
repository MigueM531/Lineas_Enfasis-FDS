class Coordinador:
    def __init__(self, id_coordinador, nombre):
        self.id_coordinador = id_coordinador
        self.nombre = nombre

    def aprobar_oferta(self, curso):
        curso.estado = "aprobado"
        return f"Curso {curso.nombre} aprobado"

    def modificar_curso(self, curso, nuevo_nombre=None, nuevo_cupo=None):
        if nuevo_nombre:
            curso.nombre = nuevo_nombre
        if nuevo_cupo:
            curso.cupo = nuevo_cupo
        return f"Curso {curso.codigo} modificado"
