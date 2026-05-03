-- =========================
-- BORRAR Y RECREAR LA BASE
-- =========================
USE master;
GO

ALTER DATABASE Crypto SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
GO

DROP DATABASE IF EXISTS Crypto;
GO

CREATE DATABASE Crypto;
GO

USE Crypto;
GO

-- =========================
-- TABLA ESTATUS
-- =========================
CREATE TABLE Estatus (
    id_estatus     INT         NOT NULL IDENTITY(1,1),
    nombre_estatus VARCHAR(20) NOT NULL,
    CONSTRAINT pk_estatus        PRIMARY KEY (id_estatus),
    CONSTRAINT uq_estatus_nombre UNIQUE      (nombre_estatus),
    CONSTRAINT ck_estatus_valor  CHECK       (nombre_estatus IN ('activo', 'inactivo', 'desactivado'))
);

INSERT INTO Estatus (nombre_estatus) VALUES ('activo'), ('inactivo'), ('desactivado');

-- =========================
-- TABLA USUARIO
-- =========================
CREATE TABLE Usuario (
    id_usuario      INT          NOT NULL IDENTITY(1,1),
    nombre_completo VARCHAR(100) NOT NULL,
    username        VARCHAR(50)  NOT NULL,
    rol             VARCHAR(50)  NOT NULL,
    id_estatus      INT          NOT NULL CONSTRAINT df_usuario_estatus DEFAULT 1,
    CONSTRAINT pk_usuario          PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuario_username UNIQUE      (username),
    CONSTRAINT ck_usuario_rol      CHECK       (rol IN ('control_escolar', 'profesor', 'director', 'estudiante')),
    CONSTRAINT fk_usuario_estatus  FOREIGN KEY (id_estatus)
        REFERENCES Estatus(id_estatus)
        ON UPDATE CASCADE
        ON DELETE NO ACTION
);

-- =========================
-- TABLA ESTUDIANTE
-- campos de dirección, telefono y fecha_nacimiento cifrados con AES-128-GCM
-- estructura por campo: nonce(16) + tag(16) + ciphertext
-- =========================
CREATE TABLE Estudiante (
    id_estudiante    INT            NOT NULL IDENTITY(1,1),
    calle            VARBINARY(256),  -- ej: "Av. Insurgentes 123 Int. 4"
    colonia          VARBINARY(256),  -- ej: "Hipódromo Condesa"
    codigo_postal    VARBINARY(64),   -- 5 dígitos cifrados
    telefono         VARBINARY(128),  -- ej: "+52 55 1234 5678"
    fecha_nacimiento VARBINARY(64),   -- DATE serializado como string cifrado
    id_usuario       INT            NOT NULL,
    CONSTRAINT pk_estudiante         PRIMARY KEY (id_estudiante),
    CONSTRAINT uq_estudiante_usuario UNIQUE      (id_usuario),
    CONSTRAINT fk_estudiante_usuario FOREIGN KEY (id_usuario)
        REFERENCES Usuario(id_usuario)
        ON UPDATE CASCADE
        ON DELETE NO ACTION
);

CREATE TABLE Profesor (
    id_profesor  INT NOT NULL IDENTITY(1,1),
    id_usuario   INT NOT NULL,
    id_grupo     INT NOT NULL,
    CONSTRAINT pk_profesor         PRIMARY KEY (id_profesor),
    CONSTRAINT uq_profesor_usuario UNIQUE      (id_usuario),  -- 1 usuario = 1 profesor
    CONSTRAINT uq_profesor_grupo   UNIQUE      (id_grupo),    -- 1 grupo   = 1 titular
    CONSTRAINT fk_profesor_usuario FOREIGN KEY (id_usuario) 
        REFERENCES Usuario(id_usuario)
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_profesor_grupo   FOREIGN KEY (id_grupo)   
        REFERENCES Grupo(id_grupo)
        ON UPDATE CASCADE ON DELETE NO ACTION
);

-- =========================
-- TABLA CURSO
-- =========================
CREATE TABLE Curso (
    id_curso     INT          NOT NULL IDENTITY(1,1),
    nombre_curso VARCHAR(100) NOT NULL,
    id_estatus   INT          NOT NULL CONSTRAINT df_curso_estatus DEFAULT 1,
    CONSTRAINT pk_curso         PRIMARY KEY (id_curso),
    CONSTRAINT uq_curso_nombre  UNIQUE      (nombre_curso),
    CONSTRAINT fk_curso_estatus FOREIGN KEY (id_estatus)
        REFERENCES Estatus(id_estatus)
        ON UPDATE CASCADE
        ON DELETE NO ACTION
);

-- =========================
-- TABLA CALIFICACION
-- calificacion cifrada con AES-128-GCM
-- validación de rango (0-100) se aplica en capa de aplicación al descifrar
-- =========================
CREATE TABLE Calificacion (
    id_calificacion INT            NOT NULL IDENTITY(1,1),
    calificacion    VARBINARY(128) NOT NULL,
    id_estudiante   INT            NOT NULL,
    id_curso        INT            NOT NULL,
    CONSTRAINT pk_calificacion            PRIMARY KEY (id_calificacion),
    CONSTRAINT uq_cal_estudiante_curso    UNIQUE      (id_estudiante, id_curso),
    CONSTRAINT fk_calificacion_estudiante FOREIGN KEY (id_estudiante)
        REFERENCES Estudiante(id_estudiante)
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT fk_calificacion_curso      FOREIGN KEY (id_curso)
        REFERENCES Curso(id_curso)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

-- =========================
-- TABLA NIVEL
-- =========================
CREATE TABLE Nivel (
    id_nivel     INT         NOT NULL IDENTITY(1,1),
    nombre_nivel VARCHAR(50) NOT NULL,
    CONSTRAINT pk_nivel        PRIMARY KEY (id_nivel),
    CONSTRAINT uq_nivel_nombre UNIQUE      (nombre_nivel)
);

-- =========================
-- TABLA GRUPO
-- =========================
CREATE TABLE Grupo (
    id_grupo     INT         NOT NULL IDENTITY(1,1),
    nombre_grupo VARCHAR(50) NOT NULL,
    id_nivel     INT         NOT NULL,
    CONSTRAINT pk_grupo              PRIMARY KEY (id_grupo),
    CONSTRAINT uq_grupo_nombre_nivel UNIQUE      (nombre_grupo, id_nivel),
    CONSTRAINT fk_grupo_nivel        FOREIGN KEY (id_nivel)
        REFERENCES Nivel(id_nivel)
        ON UPDATE CASCADE
        ON DELETE NO ACTION
);

-- =========================
-- TABLA REPORTE
-- =========================
CREATE TABLE Reporte (
    id_reporte     INT  NOT NULL IDENTITY(1,1),
    fecha          DATE NOT NULL CONSTRAINT df_reporte_fecha   DEFAULT CAST(GETDATE() AS DATE),
    firma_director VARCHAR(100),
    firma_profesor VARCHAR(100),
    id_usuario     INT  NOT NULL,
    id_grupo       INT  NOT NULL,
    id_curso       INT  NOT NULL,
    id_estatus     INT  NOT NULL CONSTRAINT df_reporte_estatus DEFAULT 1,
    CONSTRAINT pk_reporte         PRIMARY KEY (id_reporte),
    CONSTRAINT fk_reporte_usuario FOREIGN KEY (id_usuario)
        REFERENCES Usuario(id_usuario)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_reporte_grupo   FOREIGN KEY (id_grupo)
        REFERENCES Grupo(id_grupo)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_reporte_curso   FOREIGN KEY (id_curso)
        REFERENCES Curso(id_curso)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_reporte_estatus FOREIGN KEY (id_estatus)
        REFERENCES Estatus(id_estatus)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);


CREATE TABLE Auditoria (
    id_auditoria INT IDENTITY(1,1) PRIMARY KEY,

    id_usuario INT NOT NULL,
    accion VARCHAR(50) NOT NULL,          -- INSERT, UPDATE, DELETE, CREATE
    entidad VARCHAR(100) NOT NULL,        -- Ej: Estudiante
    id_entidad INT NOT NULL,

    descripcion VARCHAR(255) NULL,
    estado VARCHAR(30) NOT NULL,          -- EXITO, ERROR

    -- Cadena de integridad
    timestamp DATETIME2 NOT NULL,
    hash_anterior VARBINARY(64) NOT NULL,
    nonce UNIQUEIDENTIFIER NOT NULL,
    hash VARBINARY(64) NOT NULL,

    firma VARCHAR(MAX) NULL,

  
    fecha_firma DATETIME2 NULL,
    verificado BIT DEFAULT 0,

    CONSTRAINT FK_Auditoria_Usuario
        FOREIGN KEY (id_usuario)
        REFERENCES Usuario(id_usuario)
)

ALTER TABLE Auditoria 
ALTER COLUMN firma VARCHAR(MAX) NULL;
-- Agregar grupo al estudiante
ALTER TABLE Estudiante ADD id_grupo INT NULL;
ALTER TABLE Estudiante ADD CONSTRAINT fk_estudiante_grupo
    FOREIGN KEY (id_grupo) REFERENCES Grupo(id_grupo)
    ON UPDATE CASCADE ON DELETE NO ACTION;


-- Agregar llave puclica al usuario
ALTER TABLE Usuario ADD llave_publica VARCHAR(MAX) NULL;



SELECT * FROM Usuario
select * from Usuario
    JOIN Estudiante ON Usuario.id_usuario = Estudiante.id_usuario

SELECT * FROM Auditoria