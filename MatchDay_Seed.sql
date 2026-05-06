-- =========================================================================================
-- SCRIPT DE DATOS DE PRUEBA (SEED) - MATCHDAY - CORREGIDO
-- =========================================================================================

-- 1. LIMPIEZA TOTAL (Importante para evitar errores de duplicados)
TRUNCATE bd_matchday."Notificacion", bd_matchday."Partida_Usuario", bd_matchday."Partida", 
         bd_matchday."Equipo_Usuario", bd_matchday."Equipo", bd_matchday."Usuario_FCM", 
         bd_matchday."Datos_Bancarios", bd_matchday."Usuario", bd_matchday."Cancha", 
         bd_matchday."Region", bd_matchday."Deporte" RESTART IDENTITY CASCADE;

-- 2. DEPORTES
INSERT INTO bd_matchday."Deporte" (id_deporte, nombre_deporte, max_jugadores_deporte) VALUES 
(1, 'Fútbol 11', 22),
(2, 'Fútbol 5', 10),
(3, 'Basketball', 10),
(4, 'Tennis', 2),
(5, 'Pádel', 4),
(6, 'Volleyball', 12);

-- 3. REGIONES (Estados de Venezuela - IDs 1 al 24)
INSERT INTO bd_matchday."Region" (id_region, nombre_region) VALUES 
(1, 'Amazonas'), (2, 'Anzoátegui'), (3, 'Apure'), (4, 'Aragua'), (5, 'Barinas'), 
(6, 'Bolívar'), (7, 'Carabobo'), (8, 'Cojedes'), (9, 'Delta Amacuro'), (10, 'Distrito Capital'), 
(11, 'Falcón'), (12, 'Guárico'), (13, 'Lara'), (14, 'Mérida'), (15, 'Miranda'), 
(16, 'Monagas'), (17, 'Nueva Esparta'), (18, 'Portuguesa'), (19, 'Sucre'), (20, 'Táchira'), 
(21, 'Trujillo'), (22, 'Vargas'), (23, 'Yaracuy'), (24, 'Zulia');

-- Sincronizar la secuencia de Region después de insertar IDs manuales
SELECT setval('bd_matchday."Region_id_region_seq"', 24);

-- Sub-regiones (Ciudades - Obtendrán IDs automáticos 25, 26, etc.)
-- Caracas (ID 25), Valencia (ID 26), Maracaibo (ID 27), Barquisimeto (ID 28), Mérida (ID 29), Lechería (ID 30)
INSERT INTO bd_matchday."Region" (nombre_region, fk_id_region) VALUES 
('Caracas', 10), ('Valencia', 7), ('Maracaibo', 24), ('Barquisimeto', 13), ('Mérida', 14), ('Lechería', 2);

-- 4. CANCHAS (Usando los IDs de las ciudades recién creadas)
INSERT INTO bd_matchday."Cancha" (nombre_cancha, direccion_cancha, latitud_cancha, longitud_cancha, fk_id_region) VALUES 
('Estadio Olímpico UCV', 'Ciudad Universitaria, Caracas', 10.4891, -66.8858, 25),
('Canchas RS21 Futsal Park', 'Los Samanes, Baruta, Caracas', 10.4542, -66.8351, 15), -- Miranda (ID 15)
('Naguanagua Sport Park', 'Valencia, Carabobo', 10.2522, -68.0105, 26),
('Vereda del Lago', 'Av. El Milagro, Maracaibo, Zulia', 10.6811, -71.6033, 27),
('Complejo Deportivo San Ignacio', 'CC San Ignacio, Chacao, Caracas', 10.4905, -66.8533, 25);

-- 5. USUARIOS
-- Usuario 1 (Admin)
INSERT INTO bd_matchday."Usuario" (id_usuario, nombre_usuario, email_usuario, password_hash, telefono_usuario, url_foto_perfil, rol_usuario, reliability_score, fecha_creacion_usuario) VALUES 
(1, 'Diego Vellojin', 'vellojindiego7@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', '+584242970648', 'https://firebasestorage.googleapis.com/v0/b/matchday-68b9a.firebasestorage.app/o/user_photos%2Fphoto_1_1777577535753.jpg?alt=media&token=634c0e39-048c-4d83-b3e3-a7bb70d9f14e', 'Admin', 5.00, '2026-04-30 18:40:19.137829');

-- Usuario 2 (Standard)
INSERT INTO bd_matchday."Usuario" (id_usuario, nombre_usuario, email_usuario, password_hash, rol_usuario, reliability_score, fecha_creacion_usuario) VALUES 
(2, 'Diego Alejandro Vellojin Posso', 'davellojin.20@est.ucab.edu.ve', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Standard', 5.00, '2026-05-05 16:08:08.771609');

-- Sincronizar secuencia de Usuario
SELECT setval('bd_matchday."Usuario_id_usuario_seq"', 2);

-- Otros 20 usuarios
DO $$
BEGIN
    FOR i IN 10..30 LOOP
        INSERT INTO bd_matchday."Usuario" (nombre_usuario, email_usuario, password_hash, rol_usuario)
        VALUES ('Jugador Extra ' || i, 'jugador' || i || '@test.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Standard');
    END LOOP;
END $$;

-- 6. EQUIPOS
INSERT INTO bd_matchday."Equipo" (id_equipo, nombre_equipo, fk_id_deporte, fk_id_usuario_capitan, url_logo_equipo, max_miembros) VALUES 
(1, 'Real Madrid', 1, 1, 'https://cdn-icons-png.flaticon.com/512/3306/3306636.png', 22),
(2, 'Vellojin Basket', 3, 1, 'https://cdn-icons-png.flaticon.com/512/889/889455.png', 12),
(3, 'Vellojin Padel', 5, 1, 'https://cdn-icons-png.flaticon.com/512/2860/2860361.png', 4),
(6, 'Manchester City', 1, 2, 'https://cdn-icons-png.flaticon.com/512/3306/3306636.png', 22),
(7, 'City Basketball', 3, 2, 'https://cdn-icons-png.flaticon.com/512/889/889455.png', 12),
(8, 'City Padel Club', 5, 2, 'https://cdn-icons-png.flaticon.com/512/2860/2860361.png', 4);

SELECT setval('bd_matchday."Equipo_id_equipo_seq"', 8);

-- 7. MIEMBROS DE EQUIPOS
-- Real Madrid (11 jugadores)
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo) VALUES (1, 1, 'aceptado', 'Capitan');
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
SELECT 1, id_usuario, 'aceptado', 'Jugador' FROM bd_matchday."Usuario" WHERE email_usuario LIKE 'jugador1%';

-- Manchester City (11 jugadores)
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo) VALUES (6, 2, 'aceptado', 'Capitan');
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
SELECT 6, id_usuario, 'aceptado', 'Jugador' FROM bd_matchday."Usuario" WHERE email_usuario LIKE 'jugador2%';

-- Capitanes para el resto
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo) VALUES 
(2, 1, 'aceptado', 'Capitan'), (3, 1, 'aceptado', 'Capitan'),
(7, 2, 'aceptado', 'Capitan'), (8, 2, 'aceptado', 'Capitan');
