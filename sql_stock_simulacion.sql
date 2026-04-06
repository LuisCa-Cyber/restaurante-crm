-- ================================================================
-- STOCK SIMULADO — Marzo 2026
-- Coherente con ~535 órdenes (Bandeja Paisa, Pechuga, Pollo Fricase,
-- Lomo de Cerdo, Carne de res, Papas, Plátano, Huevo)
-- Restaurant: Carne One | c6a4eaec-867d-44c0-b753-842032ffb250
-- ================================================================

-- 1. Eliminar datos de prueba existentes
DELETE FROM stock_movements WHERE restaurant_id = 'c6a4eaec-867d-44c0-b753-842032ffb250';
DELETE FROM ingredients    WHERE restaurant_id = 'c6a4eaec-867d-44c0-b753-842032ffb250';

-- 2. Crear insumos (stock_current = estado real al cierre de marzo, tras conteo físico)
--    🔴 = 0 | 🟡 = bajo o en mínimo | 🟢 = sobre mínimo
INSERT INTO ingredients (id, restaurant_id, name, unit, stock_current, stock_min, cost_per_unit, category) VALUES
-- Carnes (alta rotación — Bandeja Paisa, Pechuga, Fricase, Lomo)
('f47ac10b-58cc-4372-a567-000000000001','c6a4eaec-867d-44c0-b753-842032ffb250','Pechuga de pollo','kg',  5,   5, 12000,'Carnes y mariscos'),  -- 🟡 en mínimo
('f47ac10b-58cc-4372-a567-000000000002','c6a4eaec-867d-44c0-b753-842032ffb250','Carne de res',   'kg',  5,   5, 18000,'Carnes y mariscos'),  -- 🟡 en mínimo
('f47ac10b-58cc-4372-a567-000000000003','c6a4eaec-867d-44c0-b753-842032ffb250','Lomo de cerdo',  'kg',  4,   3, 14000,'Carnes y mariscos'),  -- 🟢
-- Lácteos / huevo
('f47ac10b-58cc-4372-a567-000000000004','c6a4eaec-867d-44c0-b753-842032ffb250','Huevo',          'und', 18, 30,   500,'Lácteos y huevos'),   -- 🟡 bajo mínimo
-- Verduras
('f47ac10b-58cc-4372-a567-000000000005','c6a4eaec-867d-44c0-b753-842032ffb250','Papa pastusa',   'kg',  8,  10,  2000,'Verduras y hortalizas'), -- 🟡 bajo mínimo
('f47ac10b-58cc-4372-a567-000000000006','c6a4eaec-867d-44c0-b753-842032ffb250','Plátano',        'kg',  5,   8,  1500,'Verduras y hortalizas'), -- 🟡 bajo mínimo
('f47ac10b-58cc-4372-a567-000000000010','c6a4eaec-867d-44c0-b753-842032ffb250','Tomate chonto',  'kg',  4,   5,  3000,'Verduras y hortalizas'), -- 🟡 bajo mínimo
('f47ac10b-58cc-4372-a567-000000000011','c6a4eaec-867d-44c0-b753-842032ffb250','Cebolla cabezona','kg', 3,   3,  2500,'Verduras y hortalizas'), -- 🟡 en mínimo
('f47ac10b-58cc-4372-a567-000000000012','c6a4eaec-867d-44c0-b753-842032ffb250','Lechuga',        'kg',  1.5, 2,  4000,'Verduras y hortalizas'), -- 🟡 bajo mínimo
('f47ac10b-58cc-4372-a567-000000000014','c6a4eaec-867d-44c0-b753-842032ffb250','Limón',          'kg',  2,   3,  3500,'Verduras y hortalizas'), -- 🟡 bajo mínimo
-- Granos
('f47ac10b-58cc-4372-a567-000000000007','c6a4eaec-867d-44c0-b753-842032ffb250','Arroz',          'kg', 10,  10,  3500,'Granos y legumbres'),    -- 🟡 en mínimo
('f47ac10b-58cc-4372-a567-000000000008','c6a4eaec-867d-44c0-b753-842032ffb250','Frijoles',       'kg',  6,   8,  4500,'Granos y legumbres'),    -- 🟡 bajo mínimo
-- Condimentos
('f47ac10b-58cc-4372-a567-000000000009','c6a4eaec-867d-44c0-b753-842032ffb250','Aceite vegetal', 'lt',  4,   3,  8000,'Condimentos y salsas'),  -- 🟢
('f47ac10b-58cc-4372-a567-000000000013','c6a4eaec-867d-44c0-b753-842032ffb250','Sal',            'kg',  4,   2,  1200,'Condimentos y salsas'),  -- 🟢
-- Bebidas
('f47ac10b-58cc-4372-a567-000000000015','c6a4eaec-867d-44c0-b753-842032ffb250','Leche de coco',  'lt',  2,   2,  6000,'Bebidas');              -- 🟡 en mínimo


-- ================================================================
-- 3. MOVIMIENTOS — Historia completa de marzo 2026
--    Compras semanales + mermas puntuales + conteo físico 31 mar
--    Todos los timestamps en UTC (Colombia = UTC-5)
--    8:00am COL = 13:00 UTC
-- ================================================================

-- ──────────────────────────────────────────────────────────────────
-- SEMANA 1 — Compra de apertura (1 Mar, 8am COL)
-- Proveedor: Frigorífico Andino (carnes) + Mercado Central (resto)
-- ──────────────────────────────────────────────────────────────────
INSERT INTO stock_movements (id, restaurant_id, ingredient_id, type, quantity, reason, cost_per_unit, created_at) VALUES
('d8e8fca2-bdaf-11d9-9669-000000000001','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000001','entrada', 20,   'Frigorífico Andino — apertura marzo', 12000,'2026-03-01T13:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000002','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000002','entrada', 20,   'Frigorífico Andino — apertura marzo', 18000,'2026-03-01T13:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000003','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000003','entrada',  8,   'Frigorífico Andino — apertura marzo', 14000,'2026-03-01T13:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000004','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000004','entrada', 72,   'Mercado Central — apertura marzo',      500,'2026-03-01T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000005','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000005','entrada', 25,   'Mercado Central — apertura marzo',     2000,'2026-03-01T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000006','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000006','entrada', 25,   'Mercado Central — apertura marzo',     1500,'2026-03-01T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000007','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000007','entrada', 35,   'Mercado Central — apertura marzo',     3500,'2026-03-01T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000008','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000008','entrada', 12,   'Mercado Central — apertura marzo',     4500,'2026-03-01T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000009','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000009','entrada',  5,   'Mercado Central — apertura marzo',     8000,'2026-03-01T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000010','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000010','entrada', 10,   'Mercado Central — apertura marzo',     3000,'2026-03-01T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000011','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000011','entrada',  6,   'Mercado Central — apertura marzo',     2500,'2026-03-01T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000012','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000012','entrada',  4,   'Mercado Central — apertura marzo',     4000,'2026-03-01T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000013','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000013','entrada',  4,   'Mercado Central — apertura marzo',     1200,'2026-03-01T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000014','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000014','entrada',  3.5, 'Mercado Central — apertura marzo',     3500,'2026-03-01T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000015','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000015','entrada',  5,   'Mercado Central — apertura marzo',     6000,'2026-03-01T13:30:00+00:00');

-- ──────────────────────────────────────────────────────────────────
-- MERMA — 7 Mar (sábado): lechuga vencida tras semana de calor
-- ──────────────────────────────────────────────────────────────────
INSERT INTO stock_movements (id, restaurant_id, ingredient_id, type, quantity, reason, cost_per_unit, created_at) VALUES
('d8e8fca2-bdaf-11d9-9669-000000000016','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000012','merma',   -1,   'Lechuga vencida — 1 semana de calor', NULL,'2026-03-07T18:00:00+00:00');

-- ──────────────────────────────────────────────────────────────────
-- SEMANA 2 — Reposición (9 Mar, 8am COL)
-- Semana de mayor demanda (semana laboral completa)
-- ──────────────────────────────────────────────────────────────────
INSERT INTO stock_movements (id, restaurant_id, ingredient_id, type, quantity, reason, cost_per_unit, created_at) VALUES
('d8e8fca2-bdaf-11d9-9669-000000000017','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000001','entrada', 15,   'Frigorífico Andino — reposición sem. 2', 12000,'2026-03-09T13:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000018','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000002','entrada', 15,   'Frigorífico Andino — reposición sem. 2', 18000,'2026-03-09T13:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000019','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000005','entrada', 15,   'Mercado Central — reposición sem. 2',    2000,'2026-03-09T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000020','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000006','entrada', 20,   'Mercado Central — reposición sem. 2',    1500,'2026-03-09T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000021','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000007','entrada', 25,   'Mercado Central — reposición sem. 2',    3500,'2026-03-09T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000022','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000008','entrada', 10,   'Mercado Central — reposición sem. 2',    4500,'2026-03-09T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000023','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000010','entrada',  8,   'Mercado Central — reposición sem. 2',    3000,'2026-03-09T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000024','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000011','entrada',  6,   'Mercado Central — reposición sem. 2',    2500,'2026-03-09T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000025','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000012','entrada',  3,   'Mercado Central — reposición sem. 2',    4000,'2026-03-09T13:30:00+00:00');

-- ──────────────────────────────────────────────────────────────────
-- MERMA — 14 Mar (sábado): tomate aplastado en el transporte
-- ──────────────────────────────────────────────────────────────────
INSERT INTO stock_movements (id, restaurant_id, ingredient_id, type, quantity, reason, cost_per_unit, created_at) VALUES
('d8e8fca2-bdaf-11d9-9669-000000000026','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000010','merma',   -2,   'Tomate aplastado en transporte del proveedor', NULL,'2026-03-14T18:00:00+00:00');

-- ──────────────────────────────────────────────────────────────────
-- SEMANA 3 — Reposición (16 Mar, 8am COL)
-- ──────────────────────────────────────────────────────────────────
INSERT INTO stock_movements (id, restaurant_id, ingredient_id, type, quantity, reason, cost_per_unit, created_at) VALUES
('d8e8fca2-bdaf-11d9-9669-000000000027','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000001','entrada', 12,   'Frigorífico Andino — reposición sem. 3', 12000,'2026-03-16T14:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000028','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000002','entrada', 12,   'Frigorífico Andino — reposición sem. 3', 18000,'2026-03-16T14:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000029','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000003','entrada',  6,   'Frigorífico Andino — reposición sem. 3', 14000,'2026-03-16T14:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000030','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000004','entrada', 60,   'Mercado Central — reposición sem. 3',      500,'2026-03-16T14:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000031','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000005','entrada', 12,   'Mercado Central — reposición sem. 3',     2000,'2026-03-16T14:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000032','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000006','entrada', 12,   'Mercado Central — reposición sem. 3',     1500,'2026-03-16T14:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000033','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000007','entrada', 20,   'Mercado Central — reposición sem. 3',     3500,'2026-03-16T14:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000034','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000008','entrada',  6,   'Mercado Central — reposición sem. 3',     4500,'2026-03-16T14:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000035','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000009','entrada',  4,   'Mercado Central — reposición sem. 3',     8000,'2026-03-16T14:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000036','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000010','entrada',  5,   'Mercado Central — reposición sem. 3',     3000,'2026-03-16T14:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000037','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000011','entrada',  6,   'Mercado Central — reposición sem. 3',     2500,'2026-03-16T14:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000038','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000014','entrada',  3,   'Mercado Central — reposición sem. 3',     3500,'2026-03-16T14:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000039','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000015','entrada',  5,   'Mercado Central — reposición sem. 3',     6000,'2026-03-16T14:30:00+00:00');

-- ──────────────────────────────────────────────────────────────────
-- MERMA — 21 Mar (sábado): plátano maduro pasado
-- MERMA — 22 Mar (domingo): lechuga marchita
-- ──────────────────────────────────────────────────────────────────
INSERT INTO stock_movements (id, restaurant_id, ingredient_id, type, quantity, reason, cost_per_unit, created_at) VALUES
('d8e8fca2-bdaf-11d9-9669-000000000040','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000006','merma',   -3,   'Plátano demasiado maduro — no apto para servir', NULL,'2026-03-21T18:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000041','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000012','merma',   -0.5, 'Lechuga marchita fin de semana',               NULL,'2026-03-22T18:30:00+00:00');

-- ──────────────────────────────────────────────────────────────────
-- SEMANA 4 — Reposición (23 Mar, 8am COL)
-- ──────────────────────────────────────────────────────────────────
INSERT INTO stock_movements (id, restaurant_id, ingredient_id, type, quantity, reason, cost_per_unit, created_at) VALUES
('d8e8fca2-bdaf-11d9-9669-000000000042','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000001','entrada',  8,   'Frigorífico Andino — reposición sem. 4', 12000,'2026-03-23T13:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000043','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000002','entrada',  8,   'Frigorífico Andino — reposición sem. 4', 18500,'2026-03-23T13:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000044','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000005','entrada',  8,   'Mercado Central — reposición sem. 4',    2000,'2026-03-23T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000045','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000006','entrada',  8,   'Mercado Central — reposición sem. 4',    1500,'2026-03-23T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000046','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000007','entrada', 10,   'Mercado Central — reposición sem. 4',    3500,'2026-03-23T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000047','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000008','entrada',  4,   'Mercado Central — reposición sem. 4',    4500,'2026-03-23T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000048','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000010','entrada',  4,   'Mercado Central — reposición sem. 4',    3000,'2026-03-23T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000049','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000011','entrada',  4,   'Mercado Central — reposición sem. 4',    2500,'2026-03-23T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000050','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000012','entrada',  2,   'Mercado Central — reposición sem. 4',    4000,'2026-03-23T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000051','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000013','entrada',  4,   'Mercado Central — reposición sem. 4',    1200,'2026-03-23T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000052','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000014','entrada',  2,   'Mercado Central — reposición sem. 4',    3500,'2026-03-23T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000053','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000015','entrada',  4,   'Mercado Central — reposición sem. 4',    6000,'2026-03-23T13:30:00+00:00');

-- ──────────────────────────────────────────────────────────────────
-- MERMA — 28 Mar (viernes): huevos rotos en cocina
-- ──────────────────────────────────────────────────────────────────
INSERT INTO stock_movements (id, restaurant_id, ingredient_id, type, quantity, reason, cost_per_unit, created_at) VALUES
('d8e8fca2-bdaf-11d9-9669-000000000054','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000004','merma',  -12,   'Cajilla de huevos caída en cocina', NULL,'2026-03-28T17:00:00+00:00');

-- ──────────────────────────────────────────────────────────────────
-- SEMANA 5 — Compra de cierre (30 Mar, 8am COL)
-- Compra pequeña para cerrar el mes
-- ──────────────────────────────────────────────────────────────────
INSERT INTO stock_movements (id, restaurant_id, ingredient_id, type, quantity, reason, cost_per_unit, created_at) VALUES
('d8e8fca2-bdaf-11d9-9669-000000000055','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000001','entrada',  5,   'Frigorífico Andino — cierre marzo', 12000,'2026-03-30T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000056','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000002','entrada',  5,   'Frigorífico Andino — cierre marzo', 18500,'2026-03-30T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000057','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000003','entrada',  6,   'Frigorífico Andino — cierre marzo', 14000,'2026-03-30T13:30:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000058','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000005','entrada',  5,   'Mercado Central — cierre marzo',    2000,'2026-03-30T14:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000059','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000006','entrada',  5,   'Mercado Central — cierre marzo',    1600,'2026-03-30T14:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000060','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000009','entrada',  3,   'Mercado Central — cierre marzo',    8000,'2026-03-30T14:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000061','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000010','entrada',  4,   'Mercado Central — cierre marzo',    3000,'2026-03-30T14:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000062','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000011','entrada',  3,   'Mercado Central — cierre marzo',    2500,'2026-03-30T14:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000063','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000012','entrada',  2,   'Mercado Central — cierre marzo',    4200,'2026-03-30T14:00:00+00:00'),
('d8e8fca2-bdaf-11d9-9669-000000000064','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000014','entrada',  2.5, 'Mercado Central — cierre marzo',    3500,'2026-03-30T14:00:00+00:00');

-- ──────────────────────────────────────────────────────────────────
-- AJUSTE DE INVENTARIO — 31 Mar (4pm COL = 21:00 UTC)
-- Conteo físico al cerrar el mes. Descuenta el consumo real
-- de las ~535 órdenes servidas durante marzo.
-- El delta = stock_real_contado - stock_acumulado_tras_compras_y_mermas
-- ──────────────────────────────────────────────────────────────────
INSERT INTO stock_movements (id, restaurant_id, ingredient_id, type, quantity, reason, cost_per_unit, created_at) VALUES
-- Pechuga:  comprado 60kg - consumo ~55kg = 5kg reales.  delta = 5-60 = -55
('d8e8fca2-bdaf-11d9-9669-000000000065','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000001','ajuste',  -55,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Res:      comprado 60kg - consumo ~55kg = 5kg.  delta = -55
('d8e8fca2-bdaf-11d9-9669-000000000066','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000002','ajuste',  -55,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Cerdo:    comprado 20kg - consumo ~16kg = 4kg. delta = 4-20 = -16
('d8e8fca2-bdaf-11d9-9669-000000000067','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000003','ajuste',  -16,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Huevo:    comprado 132und - merma 12 = 120 disponibles - consumo 102 = 18. delta = 18-120 = -102
('d8e8fca2-bdaf-11d9-9669-000000000068','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000004','ajuste', -102,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Papa:     comprado 65kg - consumo ~57kg = 8kg. delta = 8-65 = -57
('d8e8fca2-bdaf-11d9-9669-000000000069','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000005','ajuste',  -57,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Plátano:  comprado 70 - merma 3 = 67 disponibles - consumo 62 = 5kg. delta = 5-67 = -62
('d8e8fca2-bdaf-11d9-9669-000000000070','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000006','ajuste',  -62,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Arroz:    comprado 90kg - consumo 80kg = 10kg. delta = -80
('d8e8fca2-bdaf-11d9-9669-000000000071','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000007','ajuste',  -80,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Frijoles: comprado 32kg - consumo 26kg = 6kg. delta = -26
('d8e8fca2-bdaf-11d9-9669-000000000072','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000008','ajuste',  -26,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Aceite:   comprado 12lt - consumo 8lt = 4lt. delta = -8
('d8e8fca2-bdaf-11d9-9669-000000000073','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000009','ajuste',   -8,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Tomate:   comprado 31 - merma 2 = 29 disponibles - consumo 25 = 4kg. delta = 4-29 = -25
('d8e8fca2-bdaf-11d9-9669-000000000074','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000010','ajuste',  -25,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Cebolla:  comprado 25kg - consumo 22kg = 3kg. delta = -22
('d8e8fca2-bdaf-11d9-9669-000000000075','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000011','ajuste',  -22,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Lechuga:  comprado 11 - mermas 1.5 = 9.5 disponibles - consumo 8 = 1.5kg. delta = -8
('d8e8fca2-bdaf-11d9-9669-000000000076','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000012','ajuste',   -8,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Sal:      comprado 8kg - consumo 4kg = 4kg. delta = -4
('d8e8fca2-bdaf-11d9-9669-000000000077','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000013','ajuste',   -4,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Limón:    comprado 11kg - consumo 9kg = 2kg. delta = -9
('d8e8fca2-bdaf-11d9-9669-000000000078','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000014','ajuste',   -9,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00'),
-- Leche coco: comprado 14lt - consumo 12lt = 2lt. delta = -12
('d8e8fca2-bdaf-11d9-9669-000000000079','c6a4eaec-867d-44c0-b753-842032ffb250','f47ac10b-58cc-4372-a567-000000000015','ajuste',  -12,   'Conteo físico cierre marzo — consumo del mes', NULL,'2026-03-31T21:00:00+00:00');

-- ================================================================
-- RESUMEN DE LO QUE VERÁS EN EL MÓDULO DE STOCK:
--
-- 📊 Resumen:
--   • 15 insumos totales
--   • 🟢 3 sobre el mínimo (Cerdo, Aceite, Sal)
--   • 🟡 12 en o bajo el mínimo (Pechuga, Res, Huevo, Papa,
--         Plátano, Arroz, Frijoles, Tomate, Cebolla, Lechuga,
--         Limón, Leche de coco)
--
-- 📋 Historial:
--   • 5 compras semanales (semanas del 1, 9, 16, 23, 30 marzo)
--   • 5 mermas registradas (lechuga, tomate, plátano, lechuga, huevos)
--   • 1 ajuste de inventario (conteo físico 31 marzo)
--   • Total: 79 movimientos
-- ================================================================
