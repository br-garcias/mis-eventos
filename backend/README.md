<div align="center">

# 🔌 Mis Eventos — Backend API

**API REST para la plataforma _Mis Eventos_, construida con FastAPI sobre arquitectura DDD + Hexagonal + CQRS-lite.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-8.2-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Valkey](https://img.shields.io/badge/Valkey-9-DC382D?logo=redis&logoColor=white)](https://valkey.io/)
[![Poetry](https://img.shields.io/badge/Poetry-2.x-60A5FA?logo=poetry&logoColor=white)](https://python-poetry.org/)
[![pytest](https://img.shields.io/badge/pytest-cov%E2%89%A580%25-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)
[![Ruff](https://img.shields.io/badge/lint-ruff-FCC21B)](https://docs.astral.sh/ruff/)

</div>

---

## 📖 Tabla de contenido

- [Visión general](#-visión-general)
- [Características principales](#-características-principales)
- [Stack técnico](#-stack-técnico)
- [Arquitectura](#-arquitectura)
- [Estructura del código](#-estructura-del-código)
- [Configuración (variables de entorno)](#-configuración-variables-de-entorno)
- [Ejecución local (sin Docker)](#-ejecución-local-sin-docker)
- [Ejecución con Docker](#-ejecución-con-docker)
- [Migraciones y seed](#-migraciones-y-seed)
- [Documentación de la API](#-documentación-de-la-api)
- [Autenticación y autorización](#-autenticación-y-autorización)
- [Testing y cobertura](#-testing-y-cobertura)
- [Calidad de código](#-calidad-de-código)
- [Skills `.agents/` para scaffolding DDD](#-skills-agents-para-scaffolding-ddd)
- [Decisiones técnicas](#-decisiones-técnicas)

---

## 🎯 Visión general

Backend para la gestión completa del ciclo de vida de eventos: creación, publicación, programación de sesiones, control de capacidad, registro de asistentes, autenticación con JWT y roles, búsqueda parcial, vistas optimizadas para lectura y caché en Valkey.

Diseño guiado por **Domain-Driven Design** con **separación estricta entre lectura y escritura** (CQRS-lite) y **buses de comandos/consultas** que actúan como puntos de extensión para cross-cutting concerns.

## ✨ Características principales

- 🔐 **Auth con JWT** (access + refresh con persistencia para revocación), `bcrypt`, _rate-limit_ por IP.
- 👥 **RBAC** — `admin` · `organizer` · `attendee` validados en dominio y en ruta.
- 🎟️ **Eventos** — CRUD, estados (`draft → published → cancelled`), validaciones de negocio (capacidad, fechas, ownership).
- 📅 **Sesiones** — sub-recursos con ponentes, validación de horarios y capacidad por sesión.
- 🔍 **Búsqueda** — parcial por nombre con índices Mongo (`text` + `regex` insensible a acentos).
- 📝 **Inscripciones** — concurrencia segura con _atomic counters_ sobre el aggregate.
- 📈 **CQRS** — módulos `*_views` con proyecciones de lectura (lista/detalle/perfil de usuario).
- ⚡ **Cache** — Valkey con invalidación por evento de dominio.
- 📊 **Observabilidad** — `request_id` correlacionado, _access logs_ estructurados, healthcheck.
- 📚 **OpenAPI 3.1** auto-generada (Swagger + ReDoc) con `persistAuthorization`.

---

## 🧰 Stack técnico

| Capa             | Herramientas                                                                              |
| ---------------- | ----------------------------------------------------------------------------------------- |
| Web framework    | FastAPI · Uvicorn (uvloop)                                                                |
| Validación       | Pydantic v2 (con extras `email`)                                                          |
| Persistencia     | MongoDB 8 (PyMongo síncrono)                                                              |
| Cache / sesiones | Valkey 9 (cliente `redis-py`)                                                             |
| Auth             | `python-jose[cryptography]` · `bcrypt`                                                    |
| Rate limit       | `slowapi`                                                                                 |
| Dev tooling      | Poetry · pytest · pytest-cov · pytest-mock · httpx · mongomock · fakeredis · ruff · black |

---

## 🏛️ Arquitectura

### Bounded Contexts

```
modules/
├── auth/              # login, refresh, sesiones de refresh
├── users/             # gestión de usuarios + perfil
├── roles/             # catálogo de roles
├── events/            # AGGREGATE Event (write)
├── event_sessions/    # sub-aggregate Session
├── registrations/     # inscripciones (write)
├── event_views/       # 🔍 read side (CQRS)
├── user_views/        # 🔍 read side
├── role_views/        # 🔍 read side
├── registration_views/# 🔍 read side
└── shared/            # kernel: buses, VOs, security, cache, errores
```

Cada contexto sigue la estructura **hexagonal**:

```
<context>/
├── domain/           # Aggregates, VOs, errores, puertos (repositorios)
├── application/      # Casos de uso (commands/queries + handlers + services)
│   ├── create/
│   ├── update/
│   ├── publish/
│   ├── cancel/
│   └── delete/
└── infrastructure/   # Adaptadores: Mongo, índices, mappers
```

### Flujo de un comando

```
HTTP Route
   │  (deps: auth, roles, request_id)
   ▼
Pydantic DTO ─► Command ─► CommandBus ─► Handler ─► Domain (Aggregate)
                                              │
                                              ▼
                                       Repository (port)
                                              │
                                              ▼
                                  MongoRepository (adapter)
```

### Flujo de una consulta

```
HTTP Route ─► Query ─► QueryBus ─► QueryHandler ─► ViewRepository (Mongo) ─► DTO
                                       │
                                       └── Cache (Valkey) — get/set TTL
```

---

## 📁 Estructura del código

```
backend/
├── src/
│   ├── apps/api/                 # Capa de entrega
│   │   ├── app.py                # Bootstrap FastAPI + middlewares
│   │   ├── config/               # CORS, log level, prefijos
│   │   ├── di/                   # Composition root (wire de buses + DI)
│   │   ├── middleware/           # request_context, access_log, auth, roles
│   │   ├── exception_handlers.py # Mapeo Domain → HTTP
│   │   ├── rate_limit.py
│   │   └── routes/               # auth, events, sessions, registrations, users, health
│   └── modules/                  # Bounded contexts (ver arriba)
├── tests/
│   ├── unit/                     # dominio + application puros (mongomock/fakeredis)
│   └── integration/              # API end-to-end con TestClient
├── scripts/
│   ├── migrate.py                # migraciones Mongo idempotentes versionadas
│   ├── seed.py                   # roles + admin de bootstrap
│   ├── bootstrap.py              # orquesta migrate + seed
│   └── entrypoint.sh             # arranque del contenedor
├── .agents/skills/               # 🤖 skills DDD reutilizables (ver sección)
├── Dockerfile                    # multistage Python 3.11-slim
├── pyproject.toml                # Poetry + ruff + black + pytest
└── .env.example
```

---

## ⚙️ Configuración (variables de entorno)

> Las variables se cargan desde `.env` (local) o desde `.env.api` en la raíz del repo (Docker).

| Variable            | Default                                                        | Descripción                                     |
| ------------------- | -------------------------------------------------------------- | ----------------------------------------------- |
| `JWT_SECRET`        | _(requerido)_                                                  | Llave HMAC. Generar con `openssl rand -hex 32`. |
| `JWT_ACCESS_TTL`    | `3600`                                                         | TTL del access token en segundos.               |
| `JWT_REFRESH_TTL`   | `604800`                                                       | TTL del refresh token (7 días).                 |
| `MONGO_URL`         | `mongodb://root:root@mongo:27017/mis_eventos?authSource=admin` | URL Mongo.                                      |
| `VALKEY_URL`        | `redis://valkey:6379/0`                                        | URL Valkey/Redis.                               |
| `CACHE_ENABLED`     | `true`                                                         | Activa cache de queries.                        |
| `CACHE_TTL_SECONDS` | `60`                                                           | TTL por defecto.                                |
| `API_PREFIX`        | `/api/v1`                                                      | Prefijo global de rutas.                        |
| `LOG_LEVEL`         | `INFO`                                                         | `DEBUG` · `INFO` · `WARNING` · `ERROR`.         |
| `RUN_MIGRATIONS`    | `true`                                                         | Ejecuta migraciones al arrancar el contenedor.  |
| `RUN_SEED`          | `true`                                                         | Ejecuta seed (roles + admin) al arrancar.       |

```bash
cp .env.example .env
# generar JWT_SECRET
openssl rand -hex 32
```

---

## 🚀 Ejecución local (sin Docker)

> Requisitos: Python 3.11+, Poetry 2.x, una instancia MongoDB y una de Valkey/Redis accesibles.

```bash
# 1) Lock + dependencias
poetry lock
poetry install --with dev

# 2) Configurar .env
cp .env.example .env

# 3) Migraciones + seed
poetry run python scripts/migrate.py
poetry run python scripts/seed.py

# 4) Levantar API con autoreload
poetry run uvicorn apps.api.app:app --reload --port 8000

# Nota: Es probable que necesite definir PYTHONPATH=src para que Python resuelva los módulos correctamente
PYTHONPATH=src poetry run uvicorn apps.api.app:app --reload --port 8000
PYTHONPATH=src uvicorn apps.api.app:app --reload --port 8000
```

API: http://localhost:8000 · Swagger: http://localhost:8000/docs · ReDoc: http://localhost:8000/redoc

---

## 🐳 Ejecución con Docker

Desde la **raíz del monorepo**:

```bash
docker compose up --build api mongo valkey
```

O bien usa el orquestador interactivo del proyecto:

```bash
python run.py
```

El contenedor expone `:8000` y ejecuta `entrypoint.sh` que aplica migraciones/seed según las flags `RUN_MIGRATIONS` y `RUN_SEED`.

---

## 🗃️ Migraciones y seed

- `scripts/migrate.py` — crea índices (`unique`, `text`, compuestos) e idempotentes. Cada migración registra su firma para no re-ejecutar.
- `scripts/seed.py` — crea roles base y un usuario administrador inicial.
- `scripts/bootstrap.py` — orquesta ambos en orden seguro.

```bash
poetry run python scripts/migrate.py
poetry run python scripts/seed.py
```

---

## 📚 Documentación de la API

- **Swagger UI** → `/docs` (con `persistAuthorization`)
- **ReDoc** → `/redoc`
- **OpenAPI JSON** → `/openapi.json`

Tags principales: `auth`, `users`, `events`, `event-sessions`, `registrations`, `health`.

Convenciones de respuesta de error:

```json
{
  "code": "EventNotFound",
  "message": "Event 64ab... not found",
  "request_id": "..."
}
```

---

## 🔐 Autenticación y autorización

- `POST /api/v1/auth/login` → `{access_token, refresh_token}`
- `POST /api/v1/auth/refresh` → rota tokens (revocación por sesión persistida).
- `POST /api/v1/auth/logout` → invalida refresh.
- Header: `Authorization: Bearer <access_token>`.

**Roles**: `admin`, `organizer`, `attendee`. Las rutas usan `RequireRoles(...)` como dependencia y los aggregates aplican policies de dominio (`authorization.py`) — defensa en profundidad.

### 🔒 Gestión de sesiones en Valkey — _zero-maintenance_

Las sesiones de refresh viven como claves en **Valkey con TTL nativo** (`JWT_REFRESH_TTL`). Esto aporta tres beneficios concretos:

- **Auto-limpieza:** Valkey expira las claves por sí mismo. No hay cron jobs, no hay tabla creciendo sin control, no hay "¿quién limpia esto?".
- **Revocación instantánea:** logout, rotación de password o expulsión de usuario = `DEL session:<jti>`. El refresh queda muerto en O(1), sin esperar al `exp` del JWT.
- **Multi-dispositivo:** cada sesión es una clave independiente, lo que permite "cerrar sesión en todos los dispositivos" con un simple `SCAN` + `DEL` por usuario.

El resultado: la **seguridad de un modelo con estado** (revocación real) con la **velocidad de un JWT stateless** (validación sin golpear la base de datos).

---

## 🧪 Testing y cobertura

```bash
# Toda la suite con cobertura mínima del 80%
poetry run pytest

# Sólo unit
poetry run pytest tests/unit -q

# Sólo integration
poetry run pytest tests/integration -q

# Reporte HTML
poetry run pytest --cov-report=html
open htmlcov/index.html
```

- `mongomock` para repos Mongo en unit tests → no requiere base real.
- `fakeredis` para cache en unit tests.
- Integration tests usan `TestClient` de FastAPI con dependencias inyectadas en memoria.
- `--cov-fail-under=80` configurado en `pyproject.toml` → falla el build si bajamos de 80%.

---

## 🧹 Calidad de código

```bash
poetry run ruff check src tests
poetry run ruff format src tests
poetry run black src tests
```

`ruff` con reglas `E,F,I,B,UP,N` (pyflakes + pycodestyle + bugbear + pep8-naming + pyupgrade + isort).

---

## 🤖 Skills `.agents/` para scaffolding DDD

El directorio `backend/.agents/skills/` contiene **skills declarativas** que cualquier agente AI puede consumir para generar código alineado con la arquitectura del proyecto.

| Skill                        | Propósito                                       |
| ---------------------------- | ----------------------------------------------- |
| `module-scaffolding`         | Crea un bounded context completo.               |
| `domain-layer`               | Aggregate + VOs + errores + repository port.    |
| `application-layer`          | Commands, Queries, Handlers, Services (CQRS).   |
| `infrastructure-persistence` | Repos Mongo + In-Memory + view repositories.    |
| `views-module`               | Módulo de lectura (CQRS) con proyecciones.      |
| `testing-unit`               | Templates pytest para handlers, services y VOs. |

> **Beneficio:** consistencia arquitectónica garantizada por construcción. Cualquier nuevo módulo nace con la misma forma — la deuda arquitectónica tiende a cero. Esta es la dirección que están tomando equipos top (Anthropic, Vercel, Sourcegraph) con _agent-native repositories_.

---

## 🧠 Decisiones técnicas

### MongoDB en lugar de PostgreSQL

La prueba lo permite. Mongo encaja porque:

- `Event` es jerárquico (sesiones, ponentes, capacidades por sesión).
- Las queries dominantes son lecturas filtradas por `name`, `status`, `dates` — bien resueltas con índices compuestos + `text`.
- Iteración rápida sin DDL.
- Migraciones idempotentes versionadas (`scripts/migrate.py`) con la misma garantía de orden que Alembic.

### CQRS-lite (`*_views`)

Permite optimizar lectura sin contaminar el modelo de escritura. La capa de lectura puede escalar independiente (réplicas, cache agresivo, proyecciones materializadas) sin tocar el dominio.

### Buses (Command/Query)

Aislan handlers de las rutas. Habilita decoradores transversales (logging, métricas, idempotencia, transacciones) sin tocar la capa HTTP. Inspirado en _MediatR_ (.NET) y _tactician_ (PHP).

### PyMongo síncrono (no Motor)

Concurrencia gestionada por Uvicorn con threadpool — performance suficiente, código drásticamente más simple, debugging más predecible. Migrar a async es trivial cuando lo justifique el load.

### Valkey en lugar de Redis

Fork OSS post-relicensia, mismo protocolo. Cliente `redis-py` compatible.

### Defensa en profundidad para auth

- Frontend: redirección por `RequireAuth`.
- API: `RequireRoles` como dependencia.
- Dominio: policies (`authorization.py`) que validan ownership y rol — el dominio nunca confía en la capa superior.

---

<div align="center">

📘 Volver al [README raíz](../README.md) · 📗 Ver [Frontend README](../frontend/README.md)

</div>
