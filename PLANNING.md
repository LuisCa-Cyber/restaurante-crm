# PLANNING.md — CRM Multi-Restaurante

## Idea general
CRM multi-restaurante como MVP. Una plataforma donde se gestionan
varios restaurantes desde un solo sistema. Aún sin clientes reales,
es para validar la idea.

**Stack:** Streamlit · Supabase (PostgreSQL) · OpenAI API · GitHub  
**Costo:** $0 (todos los servicios en tier gratuito)

---

## Flujo de navegación (UX)

```
Página inicial
  └── Tarjetas de restaurantes
        ├── [Soy Cliente] → Vista pública
        │     ├── Menú del restaurante
        │     └── Chat con agente IA (recomienda platos según stock real)
        └── [Soy Admin] → Pide contraseña → Panel admin
              ├── CRUD de menú
              ├── Gestión de stock e ingredientes
              ├── Registro de consumo diario
              └── Dashboard de reportes

Superadmin (rol especial)
  └── Ve todos los restaurantes + puede crear nuevos
```

---

## Estructura de carpetas

```
/
├── app.py                        # Punto de entrada
├── requirements.txt
├── PLANNING.md
├── .env.example                  # Plantilla de variables (sin secretos)
├── .gitignore
│
├── config/
│   └── settings.py               # Carga de env vars, configuración de página
│
├── database/
│   └── supabase_client.py        # Cliente Supabase singleton
│
├── pages/
│   ├── home.py                   # Página inicial con tarjetas
│   ├── cliente.py                # Vista pública del restaurante
│   └── admin.py                  # Panel de administración
│
├── ai/
│   └── agent.py                  # Agente OpenAI de recomendación
│
└── utils/
    └── auth.py                   # Verificación de contraseñas (bcrypt)
```

---

## Tablas en Supabase

| Tabla               | Descripción                                      |
|---------------------|--------------------------------------------------|
| `restaurants`       | Restaurantes registrados en la plataforma        |
| `users`             | Admins y superadmin con contraseña hasheada      |
| `menu_items`        | Platos del menú por restaurante                  |
| `ingredients`       | Ingredientes y stock disponible                  |
| `daily_consumption` | Consumo diario (descuenta stock automáticamente) |

---

## Orden de construcción

- [x] **Paso 1** — Setup: estructura de carpetas, requirements, variables de entorno
- [ ] **Paso 2** — Crear proyecto en Supabase + crear tablas con SQL
- [ ] **Paso 3** — Página inicial con tarjetas conectada a Supabase
- [ ] **Paso 4** — Flujo Cliente vs Admin (selección + login)
- [ ] **Paso 5** — Vista cliente: menú visible
- [ ] **Paso 6** — Agente IA con OpenAI (recomendaciones según stock)
- [ ] **Paso 7** — Vista admin: CRUD de menú e ingredientes
- [ ] **Paso 8** — Consumo diario + descuento automático de stock
- [ ] **Paso 9** — Dashboard de reportes (Plotly)
- [ ] **Paso 10** — Deploy en Streamlit Community Cloud

---

## Variables de entorno necesarias

| Variable              | Dónde obtenerla                          |
|-----------------------|------------------------------------------|
| `SUPABASE_URL`        | Supabase → Project Settings → API        |
| `SUPABASE_ANON_KEY`   | Supabase → Project Settings → API        |
| `OPENAI_API_KEY`      | platform.openai.com → API Keys           |
| `SUPERADMIN_PASSWORD` | La defines tú (se hashea con bcrypt)     |

En local: archivo `.env`  
En producción: Streamlit Cloud → App Settings → Secrets
