DROP TABLE IF EXISTS inscripciones CASCADE;
DROP TABLE IF EXISTS cursos CASCADE;
DROP TABLE IF EXISTS estudiantes CASCADE;
DROP TABLE IF EXISTS coordinadores CASCADE;
DROP TABLE IF EXISTS docentes CASCADE;


CREATE TABLE estudiantes (
    id_estudiante SERIAL PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    programa      VARCHAR(100) NOT NULL
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
    codigo    VARCHAR(20) PRIMARY KEY,
    nombre    VARCHAR(100) NOT NULL,
    cupo      INT NOT NULL CHECK (cupo > 0),
    semestre  INT NOT NULL CHECK (semestre > 0),
    estado    VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    id_docente INT REFERENCES docentes(id_docente) ON DELETE SET NULL
);


CREATE TABLE inscripciones (
    id SERIAL PRIMARY KEY,
    estudiante_id INT REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    curso_codigo  VARCHAR(20) REFERENCES cursos(codigo) ON DELETE CASCADE,
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (estudiante_id, curso_codigo) -- evita inscripciones duplicadas
);


CREATE INDEX idx_estudiante_programa ON estudiantes(programa);
CREATE INDEX idx_curso_semestre ON cursos(semestre);
CREATE INDEX idx_inscripcion_estudiante ON inscripciones(estudiante_id);
CREATE INDEX idx_inscripcion_curso ON inscripciones(curso_codigo);


INSERT INTO estudiantes (nombre, programa) VALUES
('Ana López', 'Ingeniería de Sistemas'),
('Carlos Pérez', 'Ingeniería Industrial');

INSERT INTO coordinadores (nombre) VALUES
('Dr. Juan Pérez');

INSERT INTO docentes (nombre) VALUES
('Msc. María Rodríguez');

