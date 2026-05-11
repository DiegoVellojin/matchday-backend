-- =========================================================================================
-- SCRIPT DE DATOS DE PRUEBA: CASOS DE PRUEBA (CAPITÁN Y JUGADOR)
-- Basado en MatchDay_db.sql y MatchDay_Seed.sql
-- =========================================================================================

-- 1. LIMPIEZA TOTAL
TRUNCATE bd_matchday."Notificacion", bd_matchday."Resultado", bd_matchday."Partida_Usuario", bd_matchday."Partida", 
         bd_matchday."Equipo_Usuario", bd_matchday."Equipo", bd_matchday."Usuario_FCM", 
         bd_matchday."Datos_Bancarios", bd_matchday."Usuario", bd_matchday."Cancha", 
         bd_matchday."Region", bd_matchday."Deporte" RESTART IDENTITY CASCADE;

-- 2. DEPORTES Y REGIONES
INSERT INTO bd_matchday."Deporte" (id_deporte, nombre_deporte, max_jugadores_deporte) VALUES (1, 'Fútbol 11', 22);
INSERT INTO bd_matchday."Region" (id_region, nombre_region) VALUES (1, 'Distrito Capital');

-- IMPORTANTE: Sincronizar la secuencia después de un insert manual
SELECT setval('bd_matchday."Region_id_region_seq"', 1);

INSERT INTO bd_matchday."Region" (nombre_region, fk_id_region) VALUES ('Caracas', 1);

-- 3. CANCHA
INSERT INTO bd_matchday."Cancha" (id_cancha, nombre_cancha, direccion_cancha, latitud_cancha, longitud_cancha, fk_id_region) VALUES 
(1, 'Estadio Olímpico UCV', 'Ciudad Universitaria, Caracas', 10.4891, -66.8858, 2);

-- 4. USUARIOS (ID 1 y 2 según lo solicitado)
INSERT INTO bd_matchday."Usuario" (id_usuario, nombre_usuario, email_usuario, password_hash, telefono_usuario, rol_usuario) VALUES 
(1, 'Capitán Diego (Org)', 'vellojindiego7@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', '+584242970648', 'Admin'),
(2, 'Capitán Alejandro (Rival)', 'davellojin.20@est.ucab.edu.ve', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', '+584123456789', 'Standard');

-- Otros jugadores para llenar el mínimo de los equipos
DO $$
BEGIN
    FOR i IN 3..30 LOOP
        INSERT INTO bd_matchday."Usuario" (id_usuario, nombre_usuario, email_usuario, password_hash, rol_usuario)
        VALUES (i, 'Jugador Test ' || i, 'jugador' || i || '@test.com', '$2b$12$LQv3c1yqBWVHxkd0LqG83eS6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U5Q6U', 'Standard');
    END LOOP;
END $$;

-- 5. DATOS BANCARIOS
INSERT INTO bd_matchday."Datos_Bancarios" (fk_id_usuario, banco, cedula, telefono) VALUES 
(1, 'Banesco', '27000001', '04242970648'),
(2, 'Mercantil', '27000002', '04123456789');

-- 6. EQUIPOS POR GRUPOS DE CASOS DE PRUEBA
-- Grupo: Negociación y Configuración
INSERT INTO bd_matchday."Equipo" (id_equipo, nombre_equipo, descripcion_equipo, fk_id_deporte, fk_id_usuario_capitan) VALUES 
(1, 'Caso 1: Configurar (Org)', 'Equipo para probar la vista inicial de configuración del capitán A', 1, 1),
(2, 'Caso 1: Rival B', 'Equipo rival para el Caso 1', 1, 2),

(3, 'Caso 5: Discrepancia A', 'Equipo para probar alerta de costos diferentes', 1, 1),
(4, 'Caso 5: Discrepancia B', 'Equipo rival con propuesta diferente', 1, 2),

-- Grupo: Vista de Jugador y Pagos
(5, 'Caso 9: Jugador Cuota A', 'Equipo para que el jugador vea su cuota calculada', 1, 1),
(6, 'Caso 9: Jugador Cuota B', 'Equipo rival en proceso de pago', 1, 2),

(7, 'Caso 10: Progreso Mixto A', 'Equipo con 5/11 pagos verificados', 1, 1),
(8, 'Caso 10: Progreso Mixto B', 'Equipo rival con 2/11 pagos', 1, 2),

(9, 'Caso 13: Pago Reportado A', 'Equipo donde el jugador ya subió su recibo', 1, 1),
(10, 'Caso 13: Pago Reportado B', 'Equipo rival', 1, 2);

-- Miembros de equipos (Mínimo 11 por equipo para pruebas de cuota)
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
SELECT id_equipo, fk_id_usuario_capitan, 'aceptado', 'Capitan' FROM bd_matchday."Equipo";

-- Llenar con jugadores extra
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
SELECT 1, id, 'aceptado', 'Jugador' FROM generate_series(3, 12) AS id;
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
SELECT 2, id, 'aceptado', 'Jugador' FROM generate_series(13, 22) AS id;
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
SELECT 5, id, 'aceptado', 'Jugador' FROM generate_series(3, 12) AS id;
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
SELECT 6, id, 'aceptado', 'Jugador' FROM generate_series(13, 22) AS id;
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
SELECT 7, id, 'aceptado', 'Jugador' FROM generate_series(3, 12) AS id;
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
SELECT 8, id, 'aceptado', 'Jugador' FROM generate_series(13, 22) AS id;
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
SELECT 9, id, 'aceptado', 'Jugador' FROM generate_series(3, 12) AS id;
INSERT INTO bd_matchday."Equipo_Usuario" (fk_id_equipo, fk_id_usuario, estatus_miembro, rol_equipo)
SELECT 10, id, 'aceptado', 'Jugador' FROM generate_series(13, 22) AS id;

-- 7. PARTIDAS POR CASO DE PRUEBA

-- PARTIDA 1: Caso Capitán - Configuración Inicial (Estado negociando, sin costos)
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b) VALUES 
(1, CURRENT_TIMESTAMP + INTERVAL '2 days', CURRENT_TIMESTAMP + INTERVAL '2 days 2 hours', 0.00, 'negociando', 1, 1, 1, 1, 2);

-- PARTIDA 2: Caso Capitán - Discrepancia de Costos
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b, propuesta_costo_a, propuesta_costo_b, propuesta_fecha_a, propuesta_fecha_b) VALUES 
(2, CURRENT_TIMESTAMP + INTERVAL '3 days', CURRENT_TIMESTAMP + INTERVAL '3 days 2 hours', 100.00, 'negociando', 1, 1, 1, 3, 4, 100.00, 120.00, CURRENT_TIMESTAMP + INTERVAL '3 days', CURRENT_TIMESTAMP + INTERVAL '3 days');

-- PARTIDA 3: Caso Jugador - Vista de Cuota y Botón "Realizar Pago" (Coincidencia exitosa)
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, fecha_acordada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b) VALUES 
(3, CURRENT_TIMESTAMP + INTERVAL '4 days', CURRENT_TIMESTAMP + INTERVAL '4 days 2 hours', CURRENT_TIMESTAMP + INTERVAL '4 days', 220.00, 'pendiente_pago', 1, 1, 1, 5, 6);

-- PARTIDA 4: Caso Jugador - Progreso de Pagos Mixto
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, fecha_acordada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b) VALUES 
(4, CURRENT_TIMESTAMP + INTERVAL '5 days', CURRENT_TIMESTAMP + INTERVAL '5 days 2 hours', CURRENT_TIMESTAMP + INTERVAL '5 days', 110.00, 'pendiente_pago', 1, 1, 1, 7, 8);

-- PARTIDA 5: Caso Jugador - Pago Reportado (Personal)
INSERT INTO bd_matchday."Partida" (id_partida, fecha_inicio_estimada, fecha_fin_estimada, fecha_acordada, costo_total_partida, estatus_partida, fk_id_usuario_org, fk_id_deporte, fk_id_cancha, fk_id_equipo_a, fk_id_equipo_b) VALUES 
(5, CURRENT_TIMESTAMP + INTERVAL '6 days', CURRENT_TIMESTAMP + INTERVAL '6 days 2 hours', CURRENT_TIMESTAMP + INTERVAL '6 days', 150.00, 'pendiente_pago', 1, 1, 1, 9, 10);

-- 8. PARTICIPANTES Y ESTADOS DE PAGO (Partida_Usuario)

-- Partida 3: Todos en pendiente para ver la cuota inicial ($220 / 2 / 11 = $10 cada uno)
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT 3, fk_id_usuario, 'pendiente', fk_id_equipo FROM bd_matchday."Equipo_Usuario" WHERE fk_id_equipo IN (5, 6);

-- Partida 4: Llenar progreso mixto
-- Equipo 7: 5 verificados
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT 4, fk_id_usuario, 'verificado', 7 FROM bd_matchday."Equipo_Usuario" WHERE fk_id_equipo = 7 LIMIT 5;
-- Equipo 7: Resto pendiente
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT 4, fk_id_usuario, 'pendiente', 7 FROM bd_matchday."Equipo_Usuario" WHERE fk_id_equipo = 7 OFFSET 5;
-- Equipo 8: 2 verificados
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT 4, fk_id_usuario, 'verificado', 8 FROM bd_matchday."Equipo_Usuario" WHERE fk_id_equipo = 8 LIMIT 2;
-- Equipo 8: Resto pendiente
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT 4, fk_id_usuario, 'pendiente', 8 FROM bd_matchday."Equipo_Usuario" WHERE fk_id_equipo = 8 OFFSET 2;

-- Partida 5: Jugador 2 (Alejandro) con pago REPORTADO
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado, url_recibo_pago, referencia_pago)
VALUES (5, 2, 'reportado', 10, 'https://firebasestorage.googleapis.com/v0/b/test/recibo.jpg', 'REF-12345');
-- Resto de la partida 5
INSERT INTO bd_matchday."Partida_Usuario" (fk_id_partida, fk_id_usuario, estatus_pago, fk_id_equipo_asignado)
SELECT 5, fk_id_usuario, 'pendiente', fk_id_equipo FROM bd_matchday."Equipo_Usuario" WHERE fk_id_equipo IN (9, 10) AND fk_id_usuario != 2;

-- 9. NOTIFICACIONES DE PRUEBA
INSERT INTO bd_matchday."Notificacion" (fk_id_usuario, mensaje, tipo, referencia_id) VALUES 
(1, 'Bienvenido Capitán. Tienes un encuentro pendiente por configurar.', 'match_negotiation', 1),
(2, 'Tienes un partido el ' || TO_CHAR(CURRENT_TIMESTAMP + INTERVAL '6 days', 'DD/MM') || '. Recuerda reportar tu pago.', 'payment_reminder', 5);

SELECT setval('bd_matchday."Usuario_id_usuario_seq"', 30);
SELECT setval('bd_matchday."Equipo_id_equipo_seq"', 10);
SELECT setval('bd_matchday."Partida_id_partida_seq"', 5);
