# 🍽️ RestauranteCRM

CRM multi-restaurante construido con Streamlit, Supabase y OpenAI. Diseñado para gestionar operaciones de restaurante en tiempo real desde cualquier dispositivo.

## ¿Qué hace?

- **Mesero** toma pedidos desde el celular, mesa por mesa, con notas por plato
- **Admin** ve todas las órdenes activas, cierra cuentas y registra ventas
- **Dashboard** de ventas filtrable por día o mes con gráficas

## Stack

| Tecnología | Uso |
|---|---|
| [Streamlit](https://streamlit.io) | Frontend e interfaz de usuario |
| [Supabase](https://supabase.com) | Base de datos PostgreSQL en la nube |
| [OpenAI API](https://openai.com) | Agente de recomendación (en desarrollo) |
| Python 3.11+ | Backend y lógica de negocio |

## Funcionalidades

### 👤 Mesero
- Selección de mesero sin login (desde lista configurada por el admin)
- Vista de mesas disponibles y ocupadas en tiempo real
- Toma de pedidos por categorías con notas por plato
- Checklist de items pendientes de entrega por mesa

### ⚙️ Administrador
- Órdenes activas en tiempo real con detalle por mesa
- Pantalla de cierre de cuenta con resumen antes de confirmar
- Tab de pendientes: todo lo que falta entregar en cada mesa
- Gestión de platos por secciones (Parrilla, Especiales, Sopas, etc.)
- Selección dinámica de platos del día
- Configuración de mesas y meseros desde la app
- Subida de imágenes a Supabase Storage

### 📊 Dashboard
- Total de ventas, número de cuentas y ticket promedio
- Gráfica de ventas por día
- Gráfica de ventas por mesero
- Tabla detalle de todas las cuentas cerradas
- Filtros por rango de fechas

## Estructura del proyecto

```
├── app.py                  # Punto de entrada
├── config/
│   └── settings.py         # Variables de entorno
├── database/
│   ├── supabase_client.py  # Cliente Supabase
│   ├── menu.py             # CRUD de platos
│   ├── orders.py           # Gestión de órdenes
│   ├── tables_db.py        # Gestión de mesas
│   ├── waiters_db.py       # Gestión de meseros
│   └── storage.py          # Subida de imágenes
├── pages/
│   ├── home.py             # Página inicial
│   ├── mesero.py           # Vista del mesero
│   └── admin.py            # Panel de administración
└── utils/
    └── auth.py             # Autenticación admin
```

## Instalación local

```bash
git clone https://github.com/LuisCa-Cyber/restaurante-crm.git
cd restaurante-crm
pip install -r requirements.txt
```

Crea un archivo `.env` basado en `.env.example`:

```
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=eyJ...
OPENAI_API_KEY=sk-...
SUPERADMIN_PASSWORD=tu-clave
```

```bash
streamlit run app.py
```

## Deploy

Desplegado en [Streamlit Community Cloud](https://streamlit.io/cloud) conectado a este repositorio. Las variables de entorno se configuran en el panel de Secrets de Streamlit Cloud.

---

Desarrollado como MVP para validar la idea de un CRM multi-restaurante.
