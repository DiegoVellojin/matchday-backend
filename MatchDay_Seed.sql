-- =========================================================================================
-- SCRIPT DE DATOS DE PRUEBA (SEED) - MATCHDAY
-- =========================================================================================

-- 1. DEPORTES
INSERT INTO bd_matchday."Deporte" (nombre_deporte, max_jugadores_deporte) VALUES 
('Fútbol 11', 22),
('Fútbol 5', 10),
('Basketball', 10),
('Tennis', 2),
('Pádel', 4),
('Volleyball', 12)
ON CONFLICT DO NOTHING;

-- 2. REGIONES (Venezuela)
INSERT INTO bd_matchday."Region" (nombre_region) VALUES 
('Distrito Capital'),
('Miranda'),
('Zulia'),
('Carabobo'),
('Lara'),
('Anzoátegui')
ON CONFLICT DO NOTHING;

INSERT INTO bd_matchday."Region" (nombre_region, fk_id_region) VALUES 
('Caracas', 1),
('Chacao', 2),
('Baruta', 2),
('Maracaibo', 3),
('Valencia', 4),
('Barquisimeto', 5),
('Lechería', 6)
ON CONFLICT DO NOTHING;

-- 3. CANCHAS DE PRUEBA (Venezuela - Con geolocalización real para Google Maps)
INSERT INTO bd_matchday."Cancha" (nombre_cancha, direccion_cancha, latitud_cancha, longitud_cancha, fk_id_region) VALUES 
('Estadio Olímpico UCV', 'Ciudad Universitaria, Caracas', 10.4891, -66.8858, 7),
('Canchas RS21 Futsal Park', 'Los Samanes, Baruta, Caracas', 10.4542, -66.8351, 9),
('Complejo Deportivo Vistamar', 'Lechería, Anzoátegui', 10.1906, -66.6911, 13),
('Vereda del Lago', 'Av. El Milagro, Maracaibo, Zulia', 10.6811, -71.6033, 10),
('Naguanagua Sport Park', 'Valencia, Carabobo', 10.2522, -68.0105, 11),
('Centro Deportivo San Ignacio', 'CC San Ignacio, Chacao, Caracas', 10.4905, -66.8533, 8)
ON CONFLICT DO NOTHING;

-- 4. USUARIOS DE PRUEBA
-- Hash para 'password123': $2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U
INSERT INTO bd_matchday."Usuario" (nombre_usuario, email_usuario, password_hash, rol_usuario, reliability_score) VALUES 
('Diego Vellojin', 'vellojindiego7@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Admin', 5.00),
('Miguel Rodriguez', 'miguel.rod@test.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Standard', 4.85),
('Gabriela Blanco', 'gabi.blanco@test.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Standard', 4.90),
('Alejandro Sosa', 'ale.sosa@test.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Standard', 4.70),
('Luis Martinez', 'luis.mtz@test.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Standard', 5.00)
ON CONFLICT (email_usuario) DO NOTHING;

-- 5. EQUIPOS DE PRUEBA
INSERT INTO bd_matchday."Equipo" (nombre_equipo, fk_id_deporte, fk_id_usuario_capitan, descripcion_equipo, esta_reclutando, max_miembros, url_logo_equipo) VALUES 
('Vinotinto del Este', 2, 1, 'Equipo de fútbol 5 en Caracas.', TRUE, 10, 'https://i.pravatar.cc/150?u=vinotinto'),
('Guerreros del Zulia', 3, 2, 'Pasión por el basket en Maracaibo.', TRUE, 12, 'https://i.pravatar.cc/150?u=guerreros'),
('Caracas Padel Club', 5, 3, 'Buscando el mejor nivel en Chacao.', FALSE, 4, 'https://i.pravatar.cc/150?u=caracas-padel'),
('Navegantes del Gol', 2, 4, 'Fútbol 5 los viernes en Lechería.', TRUE, 10, 'https://i.pravatar.cc/150?u=navegantes')
ON CONFLICT DO NOTHING;

-- 6. MIEMBROS DE EQUIPOS
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo) VALUES 
(1, 1, 'aceptado', 'Capitan'),
(1, 5, 'aceptado', 'Jugador'),
(2, 2, 'aceptado', 'Capitan'),
(3, 3, 'aceptado', 'Capitan'),
(4, 4, 'aceptado', 'Capitan'),
(4, 2, 'pendiente', 'Jugador')
ON CONFLICT DO NOTHING;

-- 7. PARTIDAS DE PRUEBA (Módulo de Partidos)
INSERT INTO bd_matchday."Partida" (
    fecha_inicio_estimada, fecha_fin_estimada, costo_total_partida, estatus_partida, 
    fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a
) VALUES 
-- Partido publicado buscando rival en Caracas
(NOW() + INTERVAL '2 days', NOW() + INTERVAL '2 days 1 hour', 45.00, 'publicada', 1, 2, 2, 1),
-- Partido en negociación en Maracaibo
(NOW() + INTERVAL '1 day', NOW() + INTERVAL '1 day 1.5 hours', 30.00, 'negociando', 2, 3, 4, 2),
-- Partido de fútbol 5 disponible en Valencia
(NOW() + INTERVAL '3 days', NOW() + INTERVAL '3 days 1 hour', 50.00, 'publicada', 4, 2, 5, 4)
ON CONFLICT DO NOTHING;

-- 8. JUGADORES EN PARTIDAS
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado) VALUES 
(1, 1, 'pendiente', 1),
(1, 5, 'pendiente', 1),
(2, 2, 'pendiente', 2),
(3, 4, 'pendiente', 4)
ON CONFLICT DO NOTHING;

-- 9. NOTIFICACIONES DE PRUEBA
INSERT INTO bd_matchday."Notificacion" (fk_id_usuario, mensaje, leida, tipo, referencia_id) VALUES 
(1, 'Tu partido en RS21 Futsal Park ha sido publicado.', FALSE, 'match_created', 1),
(2, 'Miguel, tienes una propuesta para tu partido en Vereda del Lago.', FALSE, 'negotiation_update', 2),
(5, 'Has sido convocado por Diego para el partido del domingo.', TRUE, 'invitation', 1)
ON CONFLICT DO NOTHING;
