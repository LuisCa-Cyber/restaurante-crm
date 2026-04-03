# 🍽️ RestauranteCRM

CRM multi-restaurante construido con Streamlit y Supabase. Diseñado para gestionar operaciones de restaurante en tiempo real desde cualquier dispositivo.

## ¿Qué hace?

- **Mesero** toma pedidos desde el celular, mesa por mesa, con notas y opción de sopa por plato
- **Admin** ve todas las órdenes activas en tiempo real, cierra cuentas y puede modificar totales antes de confirmar
- **Dashboard** de ventas filtrable por rango de fechas con gráficas, en horario Colombia (UTC-5)

## Stack

| Tecnología | Uso |
|---|---|
| [Streamlit](https://streamlit.io) | Frontend e interfaz de usuario |
| [Supabase](https://supabase.com) | Base de datos PostgreSQL en la nube |
| Python 3.11+ | Backend y lógica de negocio |

## Funcionalidades

### 👤 Mesero
- Selección de mesero sin login (desde lista configurada por el admin)
- Vista de mesas disponibles y ocupadas en tiempo real
- Solo ve los platos que el admin activó como **platos del día**
- Toma de pedidos por categorías (Sopas, Plato del día, Parrilla, Adiciones, Postres, Otros)
- Opción de sopa por plato con control de cuántos la llevan (+$2.000 c/u) — permite mezclar con sopa y sin sopa en el mismo plato
- Notas por plato (ej: sin ensalada, extra papa)
- Checklist de items pendientes de entrega con semáforo de tiempo (🟢🟡🔴)
- Auto-refresh cada 5 segundos en pendientes

### ⚙️ Administrador
- Órdenes activas con auto-refresh cada 5 segundos
- Pantalla de cierre con resumen completo antes de confirmar pago
- Modificación de total antes de cerrar (con registro de motivo)
- Tab de pendientes: todo lo que falta entregar en cada mesa, con semáforo de tiempo
- **Platos del día**: activa/desactiva qué platos ofrece el mesero cada día
- Gestión de platos por secciones con imágenes (Supabase Storage)
- Configuración de mesas y meseros desde la app (sin tocar Supabase)

### 📊 Dashboard
- Total de ventas, número de cuentas y ticket promedio
- Gráfica de ventas por día
- Gráfica de ventas por mesero (torta)
- Tabla detalle de cuentas cerradas
- Filtros por rango de fechas en horario Colombia (UTC-5)

## Tablas Supabase utilizadas

| Tabla | Descripción |
|---|---|
| `restaurants` | Restaurantes registrados y contraseña admin |
| `users` | Usuario admin por restaurante |
| `waiters` | Meseros por restaurante |
| `tables` | Mesas con estado (available / occupied) |
| `menu_items` | Platos del menú con precio, categoría, disponibilidad y flag de plato del día |
| `orders` | Órdenes por mesa (open / closed) — base del dashboard |
| `order_items` | Items individuales de cada orden con estado de entrega |
| `order_modifications` | Ajustes manuales al total antes de cerrar |

## Estructura del proyecto

```
├── app.py                  # Punto de entrada y enrutamiento
├── config/
│   └── settings.py         # Variables de entorno (.env local / st.secrets en cloud)
├── database/
│   ├── supabase_client.py  # Cliente Supabase (singleton)
│   ├── menu.py             # CRUD de platos
│   ├── orders.py           # Gestión de órdenes (con timezone Colombia)
│   ├── tables_db.py        # Gestión de mesas
│   ├── waiters_db.py       # Gestión de meseros
│   └── storage.py          # Subida de imágenes
├── pages/
│   ├── home.py             # Página inicial (selección de restaurante y rol)
│   ├── mesero.py           # Vista del mesero
│   └── admin.py            # Panel de administración (6 tabs)
└── utils/
    └── auth.py             # Autenticación admin con bcrypt
```

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

---

Desarrollado como MVP para validar la idea de un CRM multi-restaurante.
