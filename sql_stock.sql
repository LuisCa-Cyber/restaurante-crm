-- ================================================================
-- MÓDULO DE STOCK — Correr en Supabase SQL Editor
-- ================================================================

-- Tabla de ingredientes / insumos
CREATE TABLE IF NOT EXISTS ingredients (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  restaurant_id    UUID REFERENCES restaurants(id) ON DELETE CASCADE,
  name             TEXT NOT NULL,
  unit             TEXT NOT NULL,
  stock_current    DECIMAL(10,3) DEFAULT 0,
  stock_min        DECIMAL(10,3) DEFAULT 0,
  cost_per_unit    DECIMAL(10,2) DEFAULT 0,
  category         TEXT DEFAULT 'Otros',
  created_at       TIMESTAMPTZ DEFAULT now()
);

-- Tabla de movimientos de stock
CREATE TABLE IF NOT EXISTS stock_movements (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  restaurant_id    UUID REFERENCES restaurants(id) ON DELETE CASCADE,
  ingredient_id    UUID REFERENCES ingredients(id) ON DELETE CASCADE,
  type             TEXT NOT NULL CHECK (type IN ('entrada', 'salida', 'ajuste', 'merma')),
  quantity         DECIMAL(10,3) NOT NULL,
  reason           TEXT,
  cost_per_unit    DECIMAL(10,2),
  created_at       TIMESTAMPTZ DEFAULT now()
);

-- Columna de umbral crítico (si ya creaste la tabla antes, corre solo esta línea)
ALTER TABLE ingredients ADD COLUMN IF NOT EXISTS stock_critical DECIMAL(10,3) DEFAULT 0;

-- Índices para queries frecuentes
CREATE INDEX IF NOT EXISTS idx_ingredients_restaurant ON ingredients(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_restaurant ON stock_movements(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_ingredient ON stock_movements(ingredient_id);
