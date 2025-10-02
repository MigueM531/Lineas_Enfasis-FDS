DROP TABLE IF EXISTS inscripciones CASCADE;
DROP TABLE IF EXISTS estudiantes CASCADE;
DROP TABLE IF EXISTS cursos CASCADE;
DROP TABLE IF EXISTS coordinadores CASCADE;
DROP TABLE IF EXISTS docentes CASCADE;
DROP TABLE IF EXISTS notificaciones CASCADE;
DROP TABLE IF EXISTS reportes CASCADE;
DROP TABLE IF EXISTS programas CASCADE;
DROP TABLE IF EXISTS lineas_enfasis CASCADE;

-- ============================================
-- TABLAS PRINCIPALES
-- ============================================

CREATE TABLE estudiantes (
    id_estudiante SERIAL PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    programa      VARCHAR(100) NOT NULL,
    rol           VARCHAR(20) DEFAULT 'estudiante' CHECK (rol IN ('estudiante', 'coordinador'))
);

CREATE TABLE coordinadores (
    id_coordinador SERIAL PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL
);

CREATE TABLE docentes (
    id_docente SERIAL PRIMARY KEY,
    nombre     VARCHAR(100) NOT NULL
);

CREATE TABLE cursos (
    id_curso   SERIAL PRIMARY KEY,
    nombre     VARCHAR(100) NOT NULL,
    cupo       INT NOT NULL CHECK (cupo > 0),
    creditos   INT NOT NULL CHECK (creditos > 0),
    cronograma JSONB DEFAULT '[]',
    estado     VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'aprobado', 'rechazado')),
    id_docente INT REFERENCES docentes(id_docente) ON DELETE SET NULL
);

CREATE TABLE inscripciones (
    id SERIAL PRIMARY KEY,
    estudiante_id INT REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    curso_id INT REFERENCES cursos(id_curso) ON DELETE CASCADE,
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'pendiente'
);

CREATE TABLE notificaciones (
    id_notificacion SERIAL PRIMARY KEY,
    mensaje         TEXT NOT NULL,
    destinatario    VARCHAR(100) NOT NULL
);

CREATE TABLE reportes (
    id_reporte SERIAL PRIMARY KEY,
    contenido  TEXT NOT NULL
);

CREATE TABLE programas (
    id_programa SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL
);

CREATE TABLE lineas_enfasis (
    id_linea SERIAL PRIMARY KEY,
    nombre   VARCHAR(100) NOT NULL
);

-- ============================================
-- ÍNDICES
-- ============================================

CREATE INDEX idx_estudiante_programa ON estudiantes(programa);
CREATE INDEX idx_estudiante_rol ON estudiantes(rol);
CREATE INDEX idx_curso_estado ON cursos(estado);
CREATE INDEX idx_inscripcion_estudiante ON inscripciones(estudiante_id);
CREATE INDEX idx_inscripcion_curso ON inscripciones(curso_id);
