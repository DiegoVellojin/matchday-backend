-- =========================================================================================
-- SCRIPT DE BASE DE DATOS: MATCHDAY (REFACTOR NATIVO MULTIMONEDA)
-- ARQUITECTURA: Tablas en Singular (PascalCase) / Columnas en snake_case
-- =========================================================================================

DROP SCHEMA IF EXISTS bd_matchday CASCADE;
CREATE SCHEMA bd_matchday;
SET search_path TO bd_matchday;

-- =========================================================================================
-- 1. TABLAS CATÁLOGO Y CONFIGURACIÓN BASE
-- =========================================================================================

CREATE TABLE IF NOT EXISTS bd_matchday."Region"(
    id_region SERIAL PRIMARY KEY,
    nombre_region VARCHAR(100) NOT NULL,
    fk_id_region INT NULL,
    CONSTRAINT fk_region_padre FOREIGN KEY (fk_id_region) REFERENCES bd_matchday."Region"(id_region) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bd_matchday."Deporte"(
    id_deporte SERIAL PRIMARY KEY,
    nombre_deporte VARCHAR(50) NOT NULL,
    max_jugadores_deporte INT 
);

CREATE TABLE IF NOT EXISTS bd_matchday."Cancha"(
    id_cancha SERIAL PRIMARY KEY,
    nombre_cancha VARCHAR(150) NOT NULL,
    direccion_cancha TEXT,
    latitud_cancha DECIMAL(10, 8) NULL,  
    longitud_cancha DECIMAL(11, 8) NULL, 
    fk_id_region INT NOT NULL,
    CONSTRAINT fk_cancha_region FOREIGN KEY (fk_id_region) REFERENCES bd_matchday."Region"(id_region)
);

-- =========================================================================================
-- 1.5. MÓDULO FINANCIERO: HISTORIAL DE TASAS DE CAMBIO (BCV)
-- =========================================================================================

CREATE TABLE IF NOT EXISTS bd_matchday."TasaCambio"(
    id_tasa SERIAL PRIMARY KEY,
    moneda VARCHAR(3) NOT NULL, 
    monto_bs DECIMAL(12, 4) NOT NULL, 
    fecha_referencia DATE DEFAULT CURRENT_DATE NOT NULL, 
    fecha_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    fuente VARCHAR(50) DEFAULT 'BCV' NOT NULL,
    CONSTRAINT chk_tasa_moneda CHECK (moneda IN ('USD', 'EUR'))
);

-- =========================================================================================
-- 2. GESTIÓN DE USUARIOS Y EQUIPOS
-- =========================================================================================

CREATE TABLE IF NOT EXISTS bd_matchday."Usuario"(
    id_usuario SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(100) NOT NULL,
    email_usuario VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NULL,
    telefono_usuario VARCHAR(20) NULL, 
    url_foto_perfil VARCHAR(255) NULL,  
    rol_usuario VARCHAR(20) DEFAULT 'Standard' NOT NULL,  
    reliability_score DECIMAL(3, 2) DEFAULT 5.00, 
    fecha_creacion_usuario TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_rol_usuario CHECK (rol_usuario IN ('Standard', 'Admin'))
);

CREATE TABLE IF NOT EXISTS bd_matchday."Datos_Bancarios"(
    id_datos SERIAL PRIMARY KEY,
    fk_id_usuario INT NOT NULL,
    banco VARCHAR(100) NOT NULL,
    cedula VARCHAR(50) NOT NULL,
    telefono VARCHAR(50) NOT NULL,
    CONSTRAINT fk_datos_usuario FOREIGN KEY (fk_id_usuario) REFERENCES bd_matchday."Usuario"(id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bd_matchday."Equipo"(
    id_equipo SERIAL PRIMARY KEY,
    nombre_equipo VARCHAR(100) NOT NULL,
    url_logo_equipo VARCHAR(255) NULL, 
    descripcion_equipo TEXT NULL,
    esta_reclutando BOOLEAN DEFAULT TRUE,
    max_miembros INT DEFAULT 11,
    puntos_acumulados INT DEFAULT 0,  
    fecha_creacion_equipo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    url_chat_equipo VARCHAR(255) NULL,
    fk_id_deporte INT NOT NULL,
    fk_id_usuario_capitan INT NULL,
    CONSTRAINT fk_equipo_deporte FOREIGN KEY (fk_id_deporte) REFERENCES bd_matchday."Deporte"(id_deporte),
    CONSTRAINT fk_equipo_capitan FOREIGN KEY (fk_id_usuario_capitan) REFERENCES bd_matchday."Usuario"(id_usuario) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS bd_matchday."Equipo_Usuario"(
    fk_id_equipo INT NOT NULL,
    fk_id_usuario INT NOT NULL,
    estatus_miembro VARCHAR(20) DEFAULT 'pendiente' NOT NULL, 
    rol_equipo VARCHAR(20) DEFAULT 'Jugador' NOT NULL,
    PRIMARY KEY (fk_id_equipo, fk_id_usuario),
    CONSTRAINT fk_equipo_usuario_equipo FOREIGN KEY (fk_id_equipo) REFERENCES bd_matchday."Equipo"(id_equipo) ON DELETE CASCADE,
    CONSTRAINT fk_equipo_usuario_usuario FOREIGN KEY (fk_id_usuario) REFERENCES bd_matchday."Usuario"(id_usuario) ON DELETE CASCADE,
    CONSTRAINT chk_estatus_miembro CHECK (estatus_miembro IN ('pendiente', 'aceptado')),
    CONSTRAINT chk_rol_equipo CHECK (rol_equipo IN ('Capitan', 'Delegado', 'Jugador'))
);

-- =========================================================================================
-- 3. CORE DE NEGOCIO: PARTIDOS, PAGOS Y RESULTADOS
-- =========================================================================================

CREATE TABLE IF NOT EXISTS bd_matchday."Partida"(
    id_partida SERIAL PRIMARY KEY,
    fecha_inicio_estimada TIMESTAMP NOT NULL, 
    fecha_fin_estimada TIMESTAMP NOT NULL,    
    fecha_acordada TIMESTAMP NULL,          
    costo_total_partida DECIMAL(10, 2) NOT NULL,
    moneda VARCHAR(3) DEFAULT 'USD' NOT NULL,  
    cupos_totales INT DEFAULT 22 NOT NULL,     
    estatus_partida VARCHAR(20) DEFAULT 'publicada' NOT NULL,
    fecha_creacion_partida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    propuesta_fecha_a TIMESTAMP NULL,
    propuesta_costo_a DECIMAL(10, 2) NULL,
    propuesta_moneda_a VARCHAR(3) DEFAULT 'USD',
    propuesta_fecha_b TIMESTAMP NULL,
    propuesta_costo_b DECIMAL(10, 2) NULL,
    propuesta_moneda_b VARCHAR(3) DEFAULT 'USD',
    equipo_a_listo BOOLEAN DEFAULT FALSE,
    equipo_b_listo BOOLEAN DEFAULT FALSE,
    resultado_goles_a_cap_a INT NULL,
    resultado_goles_b_cap_a INT NULL,
    resultado_goles_a_cap_b INT NULL,
    resultado_goles_b_cap_b INT NULL,
    fk_id_usuario_org INT NOT NULL,
    fk_id_deporte INT NOT NULL,
    fk_id_cancha INT NOT NULL,              
    fk_id_equipo_a INT NULL,
    fk_id_equipo_b INT NULL,
    CONSTRAINT fk_partida_organizador FOREIGN KEY (fk_id_usuario_org) REFERENCES bd_matchday."Usuario"(id_usuario),
    CONSTRAINT fk_partida_deporte FOREIGN KEY (fk_id_deporte) REFERENCES bd_matchday."Deporte"(id_deporte),
    CONSTRAINT fk_partida_cancha FOREIGN KEY (fk_id_cancha) REFERENCES bd_matchday."Cancha"(id_cancha),
    CONSTRAINT fk_partida_equipo_a FOREIGN KEY (fk_id_equipo_a) REFERENCES bd_matchday."Equipo"(id_equipo),
    CONSTRAINT fk_partida_equipo_b FOREIGN KEY (fk_id_equipo_b) REFERENCES bd_matchday."Equipo"(id_equipo),
    CONSTRAINT chk_partida_moneda CHECK (moneda IN ('USD', 'EUR')),
    CONSTRAINT chk_estatus_partida CHECK (estatus_partida IN ('publicada', 'negociando', 'pendiente_pago', 'confirmada', 'completada', 'cancelada'))
);

CREATE TABLE IF NOT EXISTS bd_matchday."Partida_Usuario"(
    fk_id_partida INT NOT NULL,
    fk_id_usuario INT NOT NULL,
    estatus_pago VARCHAR(20) DEFAULT 'pendiente' NOT NULL,
    url_recibo_pago VARCHAR(255),
    referencia_pago VARCHAR(100) NULL,
    tasa_usada_bs DECIMAL(12, 4) NULL,  
    monto_pagado_bs DECIMAL(12, 2) NULL, 
    fk_id_equipo_asignado INT NULL, 
    PRIMARY KEY (fk_id_partida, fk_id_usuario),
    CONSTRAINT fk_partida_usuario_partida FOREIGN KEY (fk_id_partida) REFERENCES bd_matchday."Partida"(id_partida) ON DELETE CASCADE,
    CONSTRAINT fk_partida_usuario_usuario FOREIGN KEY (fk_id_usuario) REFERENCES bd_matchday."Usuario"(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_partida_usuario_equipo FOREIGN KEY (fk_id_equipo_asignado) REFERENCES bd_matchday."Equipo"(id_equipo),
    CONSTRAINT chk_estatus_pago CHECK (estatus_pago IN ('pendiente', 'reportado', 'verificado'))
);

CREATE TABLE IF NOT EXISTS bd_matchday."Resultado"(
    id_resultado SERIAL PRIMARY KEY,
    fk_id_partida INT NOT NULL,
    fk_id_equipo INT NOT NULL,
    goles_favor INT DEFAULT 0,
    goles_contra INT DEFAULT 0,
    puntos_obtenidos INT NOT NULL, 
    resultado_texto VARCHAR(10) NOT NULL, 
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    CONSTRAINT fk_resultado_partida FOREIGN KEY (fk_id_partida) REFERENCES bd_matchday."Partida"(id_partida) ON DELETE CASCADE,
    CONSTRAINT fk_resultado_equipo FOREIGN KEY (fk_id_equipo) REFERENCES bd_matchday."Equipo"(id_equipo) ON DELETE CASCADE,
    CONSTRAINT chk_resultado_texto CHECK (resultado_texto IN ('Victoria', 'Derrota', 'Empate')),
    CONSTRAINT unique_resultado_partida_equipo UNIQUE (fk_id_partida, fk_id_equipo)
);

-- =========================================================================================
-- 3.5. MÓDULO DE NOTIFICACIONES
-- =========================================================================================

CREATE TABLE IF NOT EXISTS bd_matchday."Notificacion"(
    id_notificacion SERIAL PRIMARY KEY,
    fk_id_usuario INT NOT NULL,
    mensaje VARCHAR(255) NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(50) NULL,
    referencia_id INT NULL,
    CONSTRAINT fk_notificacion_usuario FOREIGN KEY (fk_id_usuario) REFERENCES bd_matchday."Usuario"(id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bd_matchday."Usuario_FCM"(
    id_token SERIAL PRIMARY KEY,
    fk_id_usuario INT NOT NULL,
    fcm_token TEXT UNIQUE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_fcm FOREIGN KEY (fk_id_usuario) REFERENCES bd_matchday."Usuario"(id_usuario) ON DELETE CASCADE
);

-- =========================================================================================
-- 4. ÍNDICES ESTRATÉGICOS DE OPTIMIZACIÓN (FALTA DE INDEXACIÓN NATIVA DE FKs EN PSQL)
-- =========================================================================================

CREATE INDEX IF NOT EXISTS idx_tasa_fecha ON bd_matchday."TasaCambio"(fecha_referencia DESC);
CREATE INDEX IF NOT EXISTS idx_partida_usuario_partida ON bd_matchday."Partida_Usuario"(fk_id_partida);
CREATE INDEX IF NOT EXISTS idx_partida_equipo_a ON bd_matchday."Partida"(fk_id_equipo_a);
CREATE INDEX IF NOT EXISTS idx_partida_equipo_b ON bd_matchday."Partida"(fk_id_equipo_b);