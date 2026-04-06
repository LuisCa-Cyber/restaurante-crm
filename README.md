# 🍽️ Restaurante CRM

Sistema de gestión para restaurante construido con Streamlit y Supabase. Maneja operaciones en tiempo real desde cualquier dispositivo — meseros, cocina, caja y bodega en un solo lugar.

## ¿Qué hace?

- **Mesero** toma pedidos desde el celular, mesa por mesa, con notas y opción de sopa por plato
- **Admin** ve todas las órdenes activas en tiempo real, cierra cuentas y gestiona el negocio
- **Stock** controla inventario con alertas de reposición, costos y análisis de consumo
- **Dashboard** de ventas filtrable por fecha con gráficas en horario Colombia (UTC-5)

## Stack

| Tecnología | Uso |
|---|---|
| [Streamlit](https://streamlit.io) | Frontend e interfaz de usuario |
| [Supabase](https://supabase.com) | Base de datos PostgreSQL en la nube |
| Python 3.11+ | Backend y lógica de negocio |

## Módulos

### 👤 Mesero
- Selección de mesero sin login (desde lista configurada por el admin)
- Vista de mesas disponibles y ocupadas en tiempo real
- Solo ve los platos que el admin activó como **platos del día**
- Toma de pedidos por categorías con notas por plato
- Opción de sopa por plato (+$2.000 c/u) — permite mezclar en el mismo pedido
- Checklist de items pendientes con semáforo de tiempo (🟢🟡🔴)
- Auto-refresh cada 5 segundos

### ⚙️ Administrador (5 módulos)

#### 🍽️ Platos y Menú
- Gestión de platos con imágenes (Supabase Storage)
- Activar / desactivar **platos del día** sin editar el menú completo

#### 🛎️ Atención y Caja
- Órdenes activas con auto-refresh cada 5 segundos
- Pantalla de cierre con resumen completo antes de confirmar
- Modificación del total antes de cerrar (con registro de motivo)
- Tab de pendientes: todo lo que falta entregar en cada mesa

#### 📦 Stock e Inventario
- Registro de entradas, salidas, descartes y conteos físicos
- Dos niveles de alerta: 🟡 mínimo y 🔴 crítico por insumo
- Cálculo automático del costo al registrar una salida (regla de tres)
- Inventario y alertas agrupados por categoría
- **Análisis de costos** con filtro de fechas: total invertido, consumido y mermas

#### 🏢 Mesas y Personal
- Gestión de mesas y meseros desde la app (sin tocar Supabase)

#### 📊 Dashboard de Ventas
- KPIs: ventas totales, mesas atendidas, platos vendidos, ticket promedio
- Gráfica de ventas por día y por mesero
- Tabla de detalle de mesas atendidas
- Filtro por rango de fechas (UTC-5 Colombia)

## Tablas Supabase

| Tabla | Módulo | Descripción |
|---|---|---|
| `restaurants` | Base | Restaurante y contraseña admin |
| `waiters` | Personal | Meseros activos |
| `tables` | Personal | Mesas con estado (available / occupied) |
| `menu_items` | Menú | Platos con precio, categoría e imagen |
| `orders` | Caja | Órdenes por mesa (open / closed) |
| `order_items` | Caja | Items de cada orden con estado de entrega |
| `order_modifications` | Caja | Ajustes manuales al total |
| `ingredients` | Stock | Insumos con umbrales y costo |
| `stock_movements` | Stock | Movimientos de inventario (entrada/salida/merma/ajuste) |

## Estructura del proyecto

```
├── app.py                      # Punto de entrada y enrutamiento
│
├── config/
│   └── settings.py             # Variables de entorno
│
├── database/                   # Acceso a Supabase por módulo
│   ├── supabase_client.py
│   ├── menu.py
│   ├── orders.py
│   ├── stock_db.py
│   ├── storage.py
│   ├── tables_db.py
│   └── waiters_db.py
│
├── views/                      # Interfaz por módulo
│   ├── home.py
│   ├── mesero.py
│   ├── admin.py
│   ├── cliente.py
│   └── stock_ui.py
│
├── utils/
│   └── auth.py                 # Autenticación admin
│
└── ai/
    └── agent.py                # Agente IA (experimental)
```

> La carpeta `sql/` con las definiciones de tablas y datos de simulación está excluida del repositorio (`.gitignore`).

## Instalación local

```bash
git clone https://github.com/LuisCa-Cyber/restaurante-crm.git
cd restaurante-crm
pip install -r requirements.txt
```

Crea un archivo `.env`:

```
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPERADMIN_PASSWORD=tu-clave
```

```bash
streamlit run app.py
```

## Deploy

Desplegado en [Streamlit Community Cloud](https://streamlit.io/cloud) conectado a este repositorio. Las variables de entorno se configuran en el panel de Secrets de Streamlit Cloud.
