--Agenda-personal-inteligente
--Si lees esto, hiciste una copia correcta del repositorio.
--Odio ser jefe y odio israel

-- Tablas Independientes
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE agendas (
    id_agenda INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    color_hex VARCHAR(7) DEFAULT '#16eed9'
) ENGINE=InnoDB;

CREATE TABLE patrones_recurrencia (
    id_recurrencia INT AUTO_INCREMENT PRIMARY KEY,
    tipo_recurrencia VARCHAR(50) NOT NULL,
    intervalo INT DEFAULT 1,
    dias_repeticion VARCHAR(100) NULL,
    fecha_limite_repeticion DATE NULL
) ENGINE=InnoDB;

-- Tabla Padre para Actividades
CREATE TABLE actividades (
    id_actividad INT AUTO_INCREMENT PRIMARY KEY,
    id_agenda INT NOT NULL,
    id_categoria INT NULL,
    id_recurrencia INT NULL,
    tipo_actividad ENUM('Tarea', 'Evento', 'Compromiso') NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    prioridad ENUM('Alta', 'Media', 'Baja') DEFAULT 'Media',
    estado ENUM('Pendiente', 'En Proceso', 'Completada', 'Cancelada') DEFAULT 'Pendiente',
    FOREIGN KEY (id_agenda) REFERENCES agendas(id_agenda) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE SET NULL,
    FOREIGN KEY (id_recurrencia) REFERENCES patrones_recurrencia(id_recurrencia) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Tablas de Herencia
CREATE TABLE tareas (
    id_actividad INT PRIMARY KEY,
    fecha_vencimiento DATE NULL,
    porcentaje_avance FLOAT DEFAULT 0.0,
    FOREIGN KEY (id_actividad) REFERENCES actividades(id_actividad) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE eventos (
    id_actividad INT PRIMARY KEY,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    ubicacion VARCHAR(255) NULL,
    FOREIGN KEY (id_actividad) REFERENCES actividades(id_actividad) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE compromisos (
    id_actividad INT PRIMARY KEY,
    enlace_reunion VARCHAR(255) NULL,
    FOREIGN KEY (id_actividad) REFERENCES actividades(id_actividad) ON DELETE CASCADE
) ENGINE=InnoDB;

--Contactos y Recordatorios
CREATE TABLE contactos (
    id_contacto INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NULL,
    telefono VARCHAR(20) NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE compromiso_contacto (
    id_actividad INT NOT NULL,
    id_contacto INT NOT NULL,
    PRIMARY KEY (id_actividad, id_contacto),
    FOREIGN KEY (id_actividad) REFERENCES compromisos(id_actividad) ON DELETE CASCADE,
    FOREIGN KEY (id_contacto) REFERENCES contactos(id_contacto) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE recordatorios (
    id_recordatorio INT AUTO_INCREMENT PRIMARY KEY,
    id_actividad INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    mensaje VARCHAR(255) NOT NULL,
    enviado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_actividad) REFERENCES actividades(id_actividad) ON DELETE CASCADE
) ENGINE=InnoDB;