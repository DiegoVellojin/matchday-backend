-- =========================================================================================
-- SCRIPT DE DATOS DE PRUEBA (SEED) - MATCHDAY - SUPER COMPLETO
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
INSERT INTO bd_matchday."Usuario" (id_usuario, nombre_usuario, email_usuario, password_hash, telefono_usuario, rol_usuario, reliability_score) VALUES 
(2, 'Diego Alejandro Vellojin Posso', 'davellojin.20@est.ucab.edu.ve', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', '+584123456789', 'Standard', 4.80);

-- Otros usuarios para llenar equipos
DO $$
BEGIN
    FOR i IN 3..30 LOOP
        INSERT INTO bd_matchday."Usuario" (id_usuario, nombre_usuario, email_usuario, password_hash, rol_usuario)
        VALUES (i, 'Jugador Extra ' || i, 'jugador' || i || '@test.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Standard');
    END LOOP;
END $$;

SELECT setval('bd_matchday."Usuario_id_usuario_seq"', 30);

-- 5.1 DATOS BANCARIOS (Para que puedan configurar partidos)
INSERT INTO bd_matchday."Datos_Bancarios" (fk_id_usuario, banco, cedula, telefono) VALUES 
(1, 'Banesco', '27000001', '04242970648'),
(2, 'Mercantil', '27000002', '04123456789');

-- 6. EQUIPOS
-- Equipos de Diego (ID 1)
INSERT INTO bd_matchday."Equipo" (id_equipo, nombre_equipo, fk_id_deporte, fk_id_usuario_capitan, url_logo_equipo, max_miembros) VALUES 
(1, 'Real Madrid (FC)', 1, 1, 'https://cdn-icons-png.flaticon.com/512/3063/3063171.png', 22),
(2, 'Vellojin Basket', 3, 1, 'https://cdn-icons-png.flaticon.com/512/889/889455.png', 12),
(3, 'Galácticos 5', 2, 1, 'https://cdn-icons-png.flaticon.com/512/3306/3306636.png', 10);

-- Equipos de Diego Alejandro (ID 2)
INSERT INTO bd_matchday."Equipo" (id_equipo, nombre_equipo, fk_id_deporte, fk_id_usuario_capitan, url_logo_equipo, max_miembros) VALUES 
(6, 'Manchester City (MC)', 1, 2, 'https://cdn-icons-png.flaticon.com/512/3063/3063171.png', 22),
(7, 'City Stars Basketball', 3, 2, 'https://cdn-icons-png.flaticon.com/512/889/889455.png', 12),
(8, 'City Futsal', 2, 2, 'https://cdn-icons-png.flaticon.com/512/3306/3306636.png', 10);

SELECT setval('bd_matchday."Equipo_id_equipo_seq"', 8);

-- 7. MIEMBROS DE EQUIPOS
-- Llenar Real Madrid (Equipo 1)
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo) VALUES (1, 1, 'aceptado', 'Capitan');
DO $$
BEGIN
    FOR i IN 3..13 LOOP
        INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
        VALUES (1, i, 'aceptado', 'Jugador');
    END LOOP;
END $$;

-- Llenar Manchester City (Equipo 6)
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo) VALUES (6, 2, 'aceptado', 'Capitan');
DO $$
BEGIN
    FOR i IN 14..24 LOOP
        INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
        VALUES (6, i, 'aceptado', 'Jugador');
    END LOOP;
END $$;

-- Diego Alejandro (ID 2) también es miembro del Real Madrid (Jugador)
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo) VALUES (1, 2, 'aceptado', 'Jugador');

-- Diego (ID 1) también es miembro del Manchester City (Jugador)
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo) VALUES (6, 1, 'aceptado', 'Jugador');

-- 8. PARTIDOS (CASOS DE USO)

-- CASE 1: JUEGO PASADO (COMPLETADO)
-- Real Madrid vs Manchester City
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, fecha_acordada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b, resultado_goles_a_cap_a, resultado_goles_b_cap_a, resultado_goles_a_cap_b, resultado_goles_b_cap_b) VALUES 
(1, '2026-05-01 18:00:00', '2026-05-01 20:00:00', '2026-05-01 18:00:00', 100.00, 'completada', 1, 1, 1, 1, 6, 3, 2, 3, 2);

-- CASE 2: JUEGO POR CONFIRMAR (PUBLICADA - OFERTA)
-- Organizado por Diego (ID 1). Buscando rival.
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a) VALUES 
(2, '2026-05-15 10:00:00', '2026-05-15 12:00:00', 150.00, 'publicada', 1, 1, 2, 1);

-- CASE 3: JUEGO POR CONFIGURAR (NEGOCIANDO)
-- Diego (ID 1) vs Diego Alejandro (ID 2). Aceptado pero no configurado.
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b) VALUES 
(3, '2026-05-18 19:00:00', '2026-05-18 21:00:00', 120.00, 'negociando', 1, 1, 5, 1, 6);

-- CASE 4: JUEGO POR PAGAR (PENDIENTE_PAGO - NADIE HA PAGADO)
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, fecha_acordada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b) VALUES 
(4, '2026-05-20 20:00:00', '2026-05-20 22:00:00', '2026-05-20 20:00:00', 200.00, 'pendiente_pago', 1, 1, 1, 1, 6);

-- CASE 5: JUEGO CON COMPAÑEROS QUE PAGARON (REAL MADRID COMPLETO, CITY PENDIENTE)
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, fecha_acordada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b) VALUES 
(5, '2026-05-22 17:00:00', '2026-05-22 19:00:00', '2026-05-22 17:00:00', 100.00, 'pendiente_pago', 1, 1, 2, 1, 6);

-- CASE 6: ALGUNOS PAGARON, OTROS EN ESPERA (MIXTO)
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, fecha_acordada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b) VALUES 
(6, '2026-05-25 15:00:00', '2026-05-25 17:00:00', '2026-05-25 15:00:00', 100.00, 'pendiente_pago', 1, 1, 3, 1, 6);

-- CASE 7: ESPERA DE RESULTADOS (CONFIRMADA Y EN TIEMPO)
-- Diego Alejandro (ID 2) es el organizador aquí para variar
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, fecha_acordada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b, equipo_a_listo, equipo_b_listo) VALUES 
(7, '2026-05-06 10:00:00', '2026-05-06 12:00:00', '2026-05-06 10:00:00', 100.00, 'confirmada', 2, 1, 1, 6, 1, true, true);

-- CASE 8: VISTA DE JUGADOR (DIEGO ES JUGADOR, ALEJANDRO ES CAPITÁN)
-- Partido donde Diego (1) es simplemente un jugador del equipo de Alejandro (6)
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, fecha_acordada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b) VALUES 
(8, '2026-05-28 18:00:00', '2026-05-28 20:00:00', '2026-05-28 18:00:00', 100.00, 'pendiente_pago', 2, 1, 1, 6, 1);

SELECT setval('bd_matchday."Partida_id_partida_seq"', 8);

-- 9. PARTICIPANTES Y PAGOS (Partida_Usuario)

-- Partida 1 (Completada): Todos verificados
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT DISTINCT ON (fk_id_usuario) 1, fk_id_usuario, 'verificado', fk_id_equipo 
FROM bd_matchday."Equipo_Usuario" 
WHERE fk_id_equipo IN (1, 6)
ORDER BY fk_id_usuario, (CASE WHEN rol_equipo = 'Capitan' THEN 0 ELSE 1 END);

-- Partida 4 (Pendiente Pago): Nadie ha pagado
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT DISTINCT ON (fk_id_usuario) 4, fk_id_usuario, 'pendiente', fk_id_equipo 
FROM bd_matchday."Equipo_Usuario" 
WHERE fk_id_equipo IN (1, 6)
ORDER BY fk_id_usuario, (CASE WHEN rol_equipo = 'Capitan' THEN 0 ELSE 1 END);

-- Partida 5 (Real Madrid full pagado, City pendiente)
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT DISTINCT ON (fk_id_usuario) 5, fk_id_usuario, 
    (CASE WHEN fk_id_equipo = 1 THEN 'verificado' ELSE 'pendiente' END), -- Team 1 paid, Team 6 pending
    fk_id_equipo 
FROM bd_matchday."Equipo_Usuario" 
WHERE fk_id_equipo IN (1, 6)
ORDER BY fk_id_usuario, (CASE WHEN rol_equipo = 'Capitan' THEN 0 ELSE 1 END);

-- Partida 6 (Mixto: Diego reportado, otros pendiente o verificado)
-- Capitanes reportados
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado, url_recibo_pago) VALUES 
(6, 1, 'reportado', 1, 'https://example.com/recibo1.jpg'),
(6, 2, 'reportado', 6, 'https://example.com/recibo2.jpg');
-- 5 de cada equipo verificado
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT 6, id_usuario, 'verificado', 1 FROM bd_matchday."Usuario" WHERE id_usuario BETWEEN 3 AND 7;
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT 6, id_usuario, 'verificado', 6 FROM bd_matchday."Usuario" WHERE id_usuario BETWEEN 14 AND 18;
-- Resto pendiente
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT 6, id_usuario, 'pendiente', 1 FROM bd_matchday."Usuario" WHERE id_usuario BETWEEN 8 AND 13;
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT 6, id_usuario, 'pendiente', 6 FROM bd_matchday."Usuario" WHERE id_usuario BETWEEN 19 AND 24;

-- Partida 7 (Espera de Resultados - Todos pagaron)
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT DISTINCT ON (fk_id_usuario) 7, fk_id_usuario, 'verificado', fk_id_equipo 
FROM bd_matchday."Equipo_Usuario" 
WHERE fk_id_equipo IN (1, 6)
ORDER BY fk_id_usuario, (CASE WHEN rol_equipo = 'Capitan' THEN 0 ELSE 1 END);

-- Partida 8 (Vista Jugador - Diego es jugador en equipo de Alejandro)
-- Alejandro Capitán Org (ID 2), Diego Jugador en equipo B (ID 1)
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT DISTINCT ON (fk_id_usuario) 8, fk_id_usuario, 'pendiente', fk_id_equipo 
FROM bd_matchday."Equipo_Usuario" 
WHERE fk_id_equipo IN (1, 6)
ORDER BY fk_id_usuario, (CASE WHEN rol_equipo = 'Capitan' THEN 0 ELSE 1 END);

-- 10. RESULTADOS (Para la partida completada)
INSERT INTO bd_matchday."Resultado" (fk_id_partida, fk_id_equipo, goles_favor, goles_contra, puntos_obtenidos, resultado_texto) VALUES 
(1, 1, 3, 2, 3, 'Victoria'),
(1, 6, 2, 3, 0, 'Derrota');

-- 11. NOTIFICACIONES PARA DIEGO (ID 1)
INSERT INTO bd_matchday."Notificacion" (fk_id_usuario, mensaje, tipo, referencia_id) VALUES 
(1, 'Tu equipo Real Madrid tiene un nuevo partido confirmado para el 22/05.', 'match_confirmed', 5),
(1, 'Tienes un pago pendiente por verificar en el partido del 25/05.', 'payment_pending', 6),
(1, 'Diego Alejandro ha aceptado tu invitación a jugar el 18/05.', 'match_accepted', 3),
(1, '¡Victoria! Tu equipo ganó 3-2 contra Manchester City.', 'match_finished', 1);

-- 12. NOTIFICACIONES PARA DIEGO ALEJANDRO (ID 2)
INSERT INTO bd_matchday."Notificacion" (fk_id_usuario, mensaje, tipo, referencia_id) VALUES 
(2, 'Diego Vellojin te ha invitado a negociar un partido.', 'match_negotiation', 3),
(2, 'Recuerda reportar tu pago para el partido del 20/05.', 'payment_reminder', 4);
