DROP TABLE IF EXISTS inscripciones CASCADE;
DROP TABLE IF EXISTS cursos CASCADE;
DROP TABLE IF EXISTS estudiantes CASCADE;
DROP TABLE IF EXISTS coordinadores CASCADE;
DROP TABLE IF EXISTS docentes CASCADE;

-- ============================================
-- CREAR TABLAS
-- ============================================

-- Tabla de estudiantes (con rol agregado)
CREATE TABLE estudiantes (
    id_estudiante SERIAL PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    programa      VARCHAR(100) NOT NULL,
    rol           VARCHAR(20) DEFAULT 'estudiante' CHECK (rol IN ('estudiante', 'coordinador'))
);

-- Tabla de coordinadores (se mantiene)
CREATE TABLE coordinadores (
    id_coordinador SERIAL PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL
);

-- Tabla de docentes (se mantiene)
CREATE TABLE docentes (
    id_docente SERIAL PRIMARY KEY,
    nombre     VARCHAR(100) NOT NULL
);

-- Tabla de cursos (se mantiene)
CREATE TABLE cursos (
    codigo     VARCHAR(20) PRIMARY KEY,
    nombre     VARCHAR(100) NOT NULL,
    cupo       INT NOT NULL CHECK (cupo > 0),
    semestre   INT NOT NULL CHECK (semestre > 0),
    estado     VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'aprobado', 'rechazado')),
    id_docente INT REFERENCES docentes(id_docente) ON DELETE SET NULL
);

-- Tabla de inscripciones (se mantiene)
CREATE TABLE inscripciones (
    id SERIAL PRIMARY KEY,
    estudiante_id INT REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    curso_codigo  VARCHAR(20) REFERENCES cursos(codigo) ON DELETE CASCADE,
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (estudiante_id, curso_codigo)
);

-- ============================================
-- ÍNDICES
-- ============================================

CREATE INDEX idx_estudiante_programa ON estudiantes(programa);
CREATE INDEX idx_estudiante_rol ON estudiantes(rol);
CREATE INDEX idx_curso_semestre ON cursos(semestre);
CREATE INDEX idx_curso_estado ON cursos(estado);
CREATE INDEX idx_inscripcion_estudiante ON inscripciones(estudiante_id);
CREATE INDEX idx_inscripcion_curso ON inscripciones(curso_codigo);

-- ============================================
-- DATOS INICIALES
-- ============================================

-- Insertar estudiantes (incluyendo coordinadores)
INSERT INTO estudiantes (nombre, programa, rol) VALUES
('Ana López', 'Ingeniería de Sistemas', 'estudiante'),
('Carlos Pérez', 'Ingeniería Industrial', 'estudiante'),
('Dr. Juan Pérez', 'Administración Académica', 'coordinador'),
('María Rodríguez', 'Ingeniería de Sistemas', 'estudiante'),
('Juan García', 'Ingeniería Electrónica', 'estudiante');

-- Insertar coordinadores (tabla separada)
INSERT INTO coordinadores (nombre) VALUES
('Dr. Juan Pérez'),
('Dra. María González'),
('Ing. Roberto Martínez');

-- Insertar docentes
INSERT INTO docentes (nombre) VALUES
('Dra. María Rodríguez'),
('PhD. Carlos Ruiz'),
('Dra. Ana López'),
('Ing. Roberto Martínez'),
('Dr. Fernando Silva');

-- Insertar cursos aprobados
INSERT INTO cursos (codigo, nombre, cupo, semestre, estado, id_docente) VALUES
('IA-501', 'Machine Learning Avanzado', 25, 2, 'aprobado', 1),
('IA-502', 'Deep Learning Aplicado', 20, 2, 'aprobado', 2),
('IA-503', 'IA para Sistemas Empresariales', 15, 2, 'aprobado', 3),
('SEG-401', 'Ciberseguridad Avanzada', 30, 2, 'aprobado', 4),
('BD-301', 'Bases de Datos NoSQL', 25, 1, 'aprobado', 5),
('WEB-201', 'Desarrollo Web Full Stack', 35, 1, 'aprobado', 1);

-- Insertar cursos pendientes de aprobación
INSERT INTO cursos (codigo, nombre, cupo, semestre, estado, id_docente) VALUES
('CC-601', 'Computación Cuántica', 15, 2, 'pendiente', 2),
('IOT-401', 'IoT y Ciudades Inteligentes', 20, 2, 'pendiente', 3);

-- Insertar inscripciones de ejemplo
INSERT INTO inscripciones (estudiante_id, curso_codigo) VALUES
(1, 'IA-501'),   -- Ana López en Machine Learning
(1, 'SEG-401'),  -- Ana López en Ciberseguridad
(2, 'BD-301'),   -- Carlos Pérez en Bases de Datos
(4, 'IA-501'),   -- María Rodríguez en Machine Learning
(4, 'WEB-201');  -- María Rodríguez en Web Full Stack

-- ============================================
-- VERIFICACIÓN
-- ============================================

-- Ver todos los estudiantes y sus roles
SELECT id_estudiante, nombre, programa, rol FROM estudiantes ORDER BY id_estudiante;

-- Ver todos los coordinadores
SELECT * FROM coordinadores ORDER BY id_coordinador;

-- Ver todos los docentes
SELECT * FROM docentes ORDER BY id_docente;

-- Ver todos los cursos con sus estados
SELECT codigo, nombre, cupo, semestre, estado, id_docente FROM cursos ORDER BY estado, semestre;

-- Ver todas las inscripciones
SELECT 
    i.id,
    e.nombre as estudiante,
    c.nombre as curso,
    c.codigo,
    i.fecha_inscripcion
FROM inscripciones i
JOIN estudiantes e ON i.estudiante_id = e.id_estudiante
JOIN cursos c ON i.curso_codigo = c.codigo
ORDER BY i.fecha_inscripcion DESC;

-- Estadísticas generales
SELECT 
    (SELECT COUNT(*) FROM estudiantes WHERE rol = 'estudiante') as total_estudiantes,
    (SELECT COUNT(*) FROM estudiantes WHERE rol = 'coordinador') as coordinadores_en_estudiantes,
    (SELECT COUNT(*) FROM coordinadores) as total_coordinadores,
    (SELECT COUNT(*) FROM docentes) as total_docentes,
    (SELECT COUNT(*) FROM cursos WHERE estado = 'aprobado') as cursos_aprobados,
    (SELECT COUNT(*) FROM cursos WHERE estado = 'pendiente') as cursos_pendientes,
    (SELECT COUNT(*) FROM inscripciones) as total_inscripciones;