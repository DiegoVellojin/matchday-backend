-- =========================================================================================
-- SCRIPT DE DATOS DE PRUEBA (SEED) - MATCHDAY
-- =========================================================================================

-- 1. DEPORTES
INSERT INTO bd_matchday."Deporte" (nombre_deporte) VALUES 
('Fútbol 11'),
('Fútbol 5'),
('Basketball'),
('Tennis'),
('Pádel'),
('Volleyball')
ON CONFLICT DO NOTHING;

-- 2. REGIONES (Ejemplos)
INSERT INTO bd_matchday."Region" (nombre_region) VALUES 
('Norte'),
('Sur'),
('Este'),
('Oeste'),
('Centro')
ON CONFLICT DO NOTHING;

-- 3. CANCHAS DE PRUEBA
INSERT INTO bd_matchday."Cancha" (nombre_cancha, direccion_cancha, fk_id_region) VALUES 
('Estadio Centenario', 'Av. Principal 123', 1),
('Polideportivo Norte', 'Calle 45 # 10-20', 1),
('Club de Tenis Elite', 'Transversal Inferior 55', 5),
('Pádel Center Pro', 'Zona Industrial Sur', 2)
ON CONFLICT DO NOTHING;

-- 4. USUARIOS DE PRUEBA
-- Nota: Las contraseñas aquí son 'password123' (hash de ejemplo, no funcional para login real si usas bcrypt)
INSERT INTO bd_matchday."Usuario" (nombre_usuario, email_usuario, password_hash, rol_usuario) VALUES 
('Diego Vellojin', 'vellojindiego7@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Admin'),
('Juan Perez', 'juan.perez@test.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Standard'),
('Maria Lopez', 'maria.lopez@test.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Standard')
ON CONFLICT (email_usuario) DO NOTHING;

-- 5. EQUIPOS DE PRUEBA
INSERT INTO bd_matchday."Equipo" (nombre_equipo, fk_id_deporte, fk_id_usuario_capitan, descripcion_equipo, esta_reclutando, max_miembros) VALUES 
('Elite Strikers FC', 1, 1, 'Buscamos ganar el torneo regional.', TRUE, 22),
('Hoops United', 3, 2, 'Pasión por el basket.', TRUE, 12),
('Padel Kings', 5, 1, 'Solo para expertos.', FALSE, 4)
ON CONFLICT DO NOTHING;

-- 6. MIEMBROS DE EQUIPOS
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo) VALUES 
(1, 1, 'aceptado', 'Capitan'),
(1, 2, 'aceptado', 'Jugador'),
(2, 2, 'aceptado', 'Capitan'),
(3, 1, 'aceptado', 'Capitan'),
(3, 3, 'pendiente', 'Jugador')
ON CONFLICT DO NOTHING;

-- 7. NOTIFICACIONES DE PRUEBA
INSERT INTO bd_matchday."Notificacion" (fk_id_usuario, mensaje, leida, tipo, referencia_id) VALUES 
(1, '¡Bienvenido a MatchDay! Empieza a crear tu equipo.', FALSE, 'welcome', NULL),
(2, 'Has sido aceptado en el equipo Elite Strikers FC.', TRUE, 'accepted', 1)
ON CONFLICT DO NOTHING;

