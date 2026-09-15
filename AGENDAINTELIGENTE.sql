# Agenda-personal-inteligente
# --Si lees esto, hiciste una copia correcta del repositorio.
# --Odio ser jefe y odio israel

-- 1:Base de Datos
CREATE DATABASE IF NOT EXISTS BD_AgendaInteligente
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE BD_AgendaInteligente;

-- 2:Tabla de Usuarios
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3:Tabla de Categorías (Trabajo, Estudio, Personal, etc.)
CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    color_hex VARCHAR(7) DEFAULT '#3B82F6'
) ENGINE=InnoDB;

-- 4:Tabla Principal de los Eventos/Tareas
CREATE TABLE eventos (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_categoria INT NULL,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NOT NULL,
    prioridad ENUM('Baja', 'Media', 'Alta') DEFAULT 'Media',
    estado ENUM('Pendiente', 'En_Proceso', 'Completado', 'Cancelado') DEFAULT 'Pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 5:Tabla de Recordatorios/Notificaciones
CREATE TABLE recordatorios (
    id_recordatorio INT AUTO_INCREMENT PRIMARY KEY,
    id_evento INT NOT NULL,
    minutos_antes INT NOT NULL DEFAULT 15,
    enviado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_evento) REFERENCES eventos(id_evento) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6:Tabla de Sugerencias de IA (Para Python más adelante)
CREATE TABLE sugerencias_ia (
    id_sugerencia INT AUTO_INCREMENT PRIMARY KEY,
    id_evento INT NOT NULL,
    tipo_sugerencia ENUM('Conflicto_Horario', 'Reorganizacion', 'Optimización_Tiempo') NOT NULL,
    mensaje_analisis TEXT NOT NULL,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_evento) REFERENCES eventos(id_evento) ON DELETE CASCADE
) ENGINE=InnoDB;