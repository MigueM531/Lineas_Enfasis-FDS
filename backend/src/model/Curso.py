class Curso:
    def __init__(self, codigo, nombre, cupo, semestre, estado="pendiente"):
        self.codigo = codigo
        self.nombre = nombre
        self.cupo = cupo
        self.semestre = semestre
        self.estado = estado

    def validar_cupo(self, inscritos):
        return inscritos < self.cupo

    def gestionar_cronograma(self):
        pass 