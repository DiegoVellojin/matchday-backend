-- =========================================================================================
-- SCRIPT DE BASE DE DATOS: MATCHDAY 
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
-- 2. GESTIÓN DE USUARIOS Y EQUIPOS
-- =========================================================================================

CREATE TABLE IF NOT EXISTS bd_matchday."Usuario"(
    id_usuario SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(100) NOT NULL,
    email_usuario VARCHAR(100) UNIQUE NOT NULL,
    telefono_usuario VARCHAR(20) NULL, 
    url_foto_perfil VARCHAR(255) NULL,  
    rol_usuario VARCHAR(20) NOT NULL,  
    reliability_score DECIMAL(3, 2) DEFAULT 5.00, 
    fecha_creacion_usuario TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bd_matchday."Equipo"(
    id_equipo SERIAL PRIMARY KEY,
    nombre_equipo VARCHAR(100) NOT NULL,
    url_logo_equipo VARCHAR(255) NULL, 
    puntos_acumulados INT DEFAULT 0,  
    fecha_creacion_equipo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fk_id_deporte INT NOT NULL,
    fk_id_usuario_capitan INT NULL,
    CONSTRAINT fk_equipo_deporte FOREIGN KEY (fk_id_deporte) REFERENCES bd_matchday."Deporte"(id_deporte),
    CONSTRAINT fk_equipo_capitan FOREIGN KEY (fk_id_usuario_capitan) REFERENCES bd_matchday."Usuario"(id_usuario) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS bd_matchday."Equipo_Usuario"(
    fk_id_equipo INT NOT NULL,
    fk_id_usuario INT NOT NULL,
    estatus_miembro VARCHAR(20) DEFAULT 'pendiente', 
    PRIMARY KEY (fk_id_equipo, fk_id_usuario),
    CONSTRAINT fk_equipo_usuario_equipo FOREIGN KEY (fk_id_equipo) REFERENCES bd_matchday."Equipo"(id_equipo) ON DELETE CASCADE,
    CONSTRAINT fk_equipo_usuario_usuario FOREIGN KEY (fk_id_usuario) REFERENCES bd_matchday."Usuario"(id_usuario) ON DELETE CASCADE
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
    estatus_partida VARCHAR(20) DEFAULT 'publicada',
    fecha_creacion_partida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fk_id_usuario_org INT NOT NULL,
    fk_id_deporte INT NOT NULL,
    fk_id_cancha INT NOT NULL,              
    fk_id_equipo_a INT NULL,
    fk_id_equipo_b INT NULL,
    CONSTRAINT fk_partida_organizador FOREIGN KEY (fk_id_usuario_org) REFERENCES bd_matchday."Usuario"(id_usuario),
    CONSTRAINT fk_partida_deporte FOREIGN KEY (fk_id_deporte) REFERENCES bd_matchday."Deporte"(id_deporte),
    CONSTRAINT fk_partida_cancha FOREIGN KEY (fk_id_cancha) REFERENCES bd_matchday."Cancha"(id_cancha),
    CONSTRAINT fk_partida_equipo_a FOREIGN KEY (fk_id_equipo_a) REFERENCES bd_matchday."Equipo"(id_equipo),
    CONSTRAINT fk_partida_equipo_b FOREIGN KEY (fk_id_equipo_b) REFERENCES bd_matchday."Equipo"(id_equipo)
);

CREATE TABLE IF NOT EXISTS bd_matchday."Partida_Usuario"(
    fk_id_partida INT NOT NULL,
    fk_id_usuario INT NOT NULL,
    estatus_pago VARCHAR(20) DEFAULT 'pendiente',
    url_recibo_pago VARCHAR(255),
    fk_id_equipo_asignado INT NULL, 
    PRIMARY KEY (fk_id_partida, fk_id_usuario),
    CONSTRAINT fk_partida_usuario_partida FOREIGN KEY (fk_id_partida) REFERENCES bd_matchday."Partida"(id_partida) ON DELETE CASCADE,
    CONSTRAINT fk_partida_usuario_usuario FOREIGN KEY (fk_id_usuario) REFERENCES bd_matchday."Usuario"(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_partida_usuario_equipo FOREIGN KEY (fk_id_equipo_asignado) REFERENCES bd_matchday."Equipo"(id_equipo)
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
    CONSTRAINT fk_resultado_equipo FOREIGN KEY (fk_id_equipo) REFERENCES bd_matchday."Equipo"(id_equipo) ON DELETE CASCADE
);

-- =========================================================================================
-- 4. RESTRICCIONES DE INTEGRIDAD Y LÓGICA DE ESTADO (CHECKS)
-- =========================================================================================

ALTER TABLE bd_matchday."Usuario" ADD CONSTRAINT chk_rol_usuario CHECK (rol_usuario IN ('Organizador', 'Jugador'));
ALTER TABLE bd_matchday."Equipo_Usuario" ADD CONSTRAINT chk_estatus_miembro CHECK (estatus_miembro IN ('pendiente', 'aceptado'));
ALTER TABLE bd_matchday."Partida" ADD CONSTRAINT chk_estatus_partida CHECK (estatus_partida IN ('publicada', 'negociando', 'pendiente_pago', 'confirmada', 'completada', 'cancelada'));
ALTER TABLE bd_matchday."Partida_Usuario" ADD CONSTRAINT chk_estatus_pago CHECK (estatus_pago IN ('pendiente', 'reportado', 'verificado'));
ALTER TABLE bd_matchday."Resultado" ADD CONSTRAINT chk_resultado_texto CHECK (resultado_texto IN ('Victoria', 'Derrota', 'Empate'));

-- =========================================================================================
-- TABLA DE PRUEBA DE CONEXIÓN
-- =========================================================================================
CREATE TABLE IF NOT EXISTS bd_matchday."LogPrueba" (
    id_log SERIAL PRIMARY KEY,
    mensaje VARCHAR(255) NOT NULL,
    origen VARCHAR(50) DEFAULT 'Backend Test',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);