-- =========================================================================================
-- SCRIPT DE DATOS DE PRUEBA SIMPLIFICADO - PARA PRUEBAS MANUALES
-- =========================================================================================

-- 1. LIMPIEZA TOTAL
TRUNCATE bd_matchday."Notificacion", bd_matchday."Resultado", bd_matchday."Partida_Usuario", bd_matchday."Partida", 
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
(6, 'Volleyball', 12),
(7, 'Béisbol', 18),
(8, 'Softbol', 20),
(9, 'Futsal', 10),
(10, 'Pickleball', 4),
(11, 'Rugby', 30),
(12, 'Ping Pong', 2);

-- 3. REGIONES
INSERT INTO bd_matchday."Region" (id_region, nombre_region) VALUES 
(1, 'Amazonas'), (2, 'Anzoátegui'), (3, 'Apure'), (4, 'Aragua'), (5, 'Barinas'), 
(6, 'Bolívar'), (7, 'Carabobo'), (8, 'Cojedes'), (9, 'Delta Amacuro'), (10, 'Distrito Capital'), 
(11, 'Falcón'), (12, 'Guárico'), (13, 'Lara'), (14, 'Mérida'), (15, 'Miranda'), 
(16, 'Monagas'), (17, 'Nueva Esparta'), (18, 'Portuguesa'), (19, 'Sucre'), (20, 'Táchira'), 
(21, 'Trujillo'), (22, 'Vargas'), (23, 'Yaracuy'), (24, 'Zulia');

SELECT setval('bd_matchday."Region_id_region_seq"', 24);

INSERT INTO bd_matchday."Region" (nombre_region, fk_id_region) VALUES 
('Caracas', 10), ('Valencia', 7), ('Maracaibo', 24), ('Barquisimeto', 13), ('Mérida', 14), ('Lechería', 2);

-- 4. CANCHAS
INSERT INTO bd_matchday."Cancha" (id_cancha, nombre_cancha, direccion_cancha, latitud_cancha, longitud_cancha, fk_id_region) VALUES 
(1, 'Estadio Olímpico UCV', 'Ciudad Universitaria, Caracas', 10.4891, -66.8858, 25),
(2, 'Canchas RS21 Futsal Park', 'Los Samanes, Baruta, Caracas', 10.4542, -66.8351, 15),
(3, 'Naguanagua Sport Park', 'Valencia, Carabobo', 10.2522, -68.0105, 26),
(4, 'Vereda del Lago', 'Av. El Milagro, Maracaibo, Zulia', 10.6811, -71.6033, 27),
(5, 'Complejo Deportivo San Ignacio', 'CC San Ignacio, Chacao, Caracas', 10.4905, -66.8533, 25);

SELECT setval('bd_matchday."Cancha_id_cancha_seq"', 5);

-- 5. USUARIOS
-- Usuario 1 (Diego - Principal)
INSERT INTO bd_matchday."Usuario" (id_usuario, nombre_usuario, email_usuario, password_hash, telefono_usuario, url_foto_perfil, rol_usuario, reliability_score) VALUES 
(1, 'Diego Vellojin', 'vellojindiego7@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', '+584242970648', 'https://firebasestorage.googleapis.com/v0/b/matchday-68b9a.firebasestorage.app/o/user_photos%2Fphoto_1_1777577535753.jpg?alt=media&token=634c0e39-048c-4d83-b3e3-a7bb70d9f14e', 'Admin', 5.00);

-- Usuario 2 (Diego Alejandro - Principal)
INSERT INTO bd_matchday."Usuario" (id_usuario, nombre_usuario, email_usuario, password_hash, telefono_usuario, url_foto_perfil, rol_usuario, reliability_score) VALUES 
(2, 'Diego Alejandro Vellojin Posso', 'davellojin.20@est.ucab.edu.ve', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', '+584123456789', 'https://firebasestorage.googleapis.com/v0/b/matchday-68b9a.firebasestorage.app/o/user_photos%2Fphoto_2_1778172042259.jpg?alt=media&token=c944b563-1ce3-4e32-b015-05599610d84b', 'Standard', 4.80);

-- Usuario 3 (Test Padel 1 - Pass: password123)
INSERT INTO bd_matchday."Usuario" (id_usuario, nombre_usuario, email_usuario, password_hash, telefono_usuario, rol_usuario, reliability_score) VALUES 
(3, 'Test Padel 1', 'padel1@test.com', '$2b$12$fZMwy/PiNnEmg8mLTu/IFOGJgCtu.ESixELligv62U3HccnqFGdlO', '+584000000001', 'Standard', 5.00);

-- Usuario 4 (Test Padel 2 - Pass: password123)
INSERT INTO bd_matchday."Usuario" (id_usuario, nombre_usuario, email_usuario, password_hash, telefono_usuario, rol_usuario, reliability_score) VALUES 
(4, 'Test Padel 2', 'padel2@test.com', '$2b$12$fZMwy/PiNnEmg8mLTu/IFOGJgCtu.ESixELligv62U3HccnqFGdlO', '+584000000002', 'Standard', 5.00);

SELECT setval('bd_matchday."Usuario_id_usuario_seq"', 4);

-- 5.1 DATOS BANCARIOS
INSERT INTO bd_matchday."Datos_Bancarios" (fk_id_usuario, banco, cedula, telefono) VALUES 
(1, 'Banesco', '27000001', '04242970648'),
(2, 'Mercantil', '27000002', '04123456789'),
(3, 'Banesco', '27000003', '04000000001'),
(4, 'Provincial', '27000004', '04000000002');
