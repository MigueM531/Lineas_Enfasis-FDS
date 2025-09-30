from database import init_db
from controller.curso_controller import CursoController
from controller.estudiante_controller import EstudianteController
from controller.coordinador_controller import CoordinadorController
from model.Estudiante import Estudiante
from model.Coordinador import Coordinador

def main():
    # Inicializar BD
    init_db()

    # Controladores
    curso_ctrl = CursoController()
    estudiante_ctrl = EstudianteController()
    coordinador_ctrl = CoordinadorController()

    # Objetos del dominio
    estudiante = Estudiante(1, "Ana López", "Ingeniería de Sistemas")
    coordinador = Coordinador(1, "Dr. Pérez")

    # Crear curso
    curso = curso_ctrl.crear_curso("MAT101", "Matemáticas Avanzadas", 30, 1)
    print(f"Curso creado: {curso.nombre} ({curso.estado})")

    # Aprobar curso
    print(coordinador_ctrl.aprobar_curso(curso))

    # Listar cursos
    for c in curso_ctrl.listar_cursos():
        print(f"- {c.codigo}: {c.nombre} ({c.estado})")

if __name__ == "__main__":
    main()
