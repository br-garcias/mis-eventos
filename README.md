<div align="center">

# 🎟️ Mis Eventos

**Plataforma full-stack para la gestión de eventos corporativos.**

</div>

---

> ### ✨ Una nota para quien revisa
>
> Gracias por tomarte el tiempo de explorar, ejecutar y evaluar este repositorio. Sé que tu tiempo es valioso, y lo aprecio sinceramente.
>
> Este repositorio busca reflejar un enfoque práctico y mantenible para un producto real con proyección de crecimiento: una arquitectura clara, buena separación de responsabilidades y una base pensada para facilitar la colaboración y evolución del equipo. Como en todo desarrollo, **siempre hay espacio para mejorar**, y cualquier comentario o sugerencia será más que bienvenido.
>
> Si encuentras algún inconveniente al ejecutar el proyecto o algo no queda del todo claro, el comando `python run.py` debería cubrir la mayoría de los casos. Y si no, estaré encantado de ayudar. 🤝

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-8.2-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Valkey](https://img.shields.io/badge/Valkey-9-DC382D?logo=redis&logoColor=white)](https://valkey.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Coverage](https://img.shields.io/badge/coverage-%E2%89%A580%25-brightgreen)](#)
[![License](https://img.shields.io/badge/license-MIT-informational)](#)

</div>

---

## 📖 Índice

- [Contexto del problema](#-contexto-del-problema)
- [Solución propuesta](#-solución-propuesta)
- [Arquitectura del sistema](#-arquitectura-del-sistema)
- [Stack tecnológico](#-stack-tecnológico)
- [Quickstart (1 comando)](#-quickstart-1-comando)
- [Setup manual por servicio](#-setup-manual-por-servicio)
- [Estructura del monorepo](#-estructura-del-monorepo)
- [Decisiones técnicas (ADR-lite)](#-decisiones-técnicas-adr-lite)
- [Skills `.agents/` — _Agent-Native Development_](#-skills-agents--agent-native-development)
- [Calidad, testing y observabilidad](#-calidad-testing-y-observabilidad)
- [Roadmap & próximos pasos](#-roadmap--próximos-pasos)

---

## 🧩 Contexto del problema

**Mis Eventos** gestiona sus eventos de forma manual: agendas en hojas de cálculo, registros por correo, sin trazabilidad y sin métricas. Esto produce desorganización, errores humanos, mala experiencia de asistentes y nula capacidad analítica.

## 💡 Solución propuesta

Una plataforma **Full-Stack** que centraliza el ciclo de vida del evento — _desde la creación, programación de sesiones y gestión de capacidad, hasta el registro de asistentes y reportería operativa_ — con **roles**, **autenticación JWT**, **API REST documentada** y **UI moderna y responsiva**.

| Eje                   | Cómo lo resolvemos                                                                              |
| --------------------- | ----------------------------------------------------------------------------------------------- |
| **Organización**      | CRUD de eventos + sesiones embebidas + búsqueda parcial por nombre indexada en Mongo.           |
| **Procesos manuales** | Inscripción 1-click con control transaccional de capacidad y estados de evento.                 |
| **Decisiones**        | Vistas CQRS optimizadas para lectura (proyecciones).                                            |
| **UX**                | Frontend React 19 + Tailwind v4, lazy-loading por ruta, skeletons, toasts y feedback inmediato. |

---

## 🏛️ Arquitectura del sistema

```
┌────────────────────────────────────────────────────────────────────────┐
│                          CLIENTE (Browser)                             │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTPS
                ┌──────────────────▼──────────────────┐
                │   Frontend · React 19 + Vite        │
                │   Feature-Sliced · Zustand · RHF    │
                └──────────────────┬──────────────────┘
                                   │ REST  /api/v1
                ┌──────────────────▼──────────────────┐
                │   API · FastAPI (CQRS + DDD)        │
                │  ┌──────────────┐  ┌──────────────┐ │
                │  │ Command Bus  │  │  Query Bus   │ │
                │  │  (write)     │  │  (read/views)│ │
                │  └──────┬───────┘  └──────┬───────┘ │
                │         │ Domain Events   │         │
                │  Aggregates · VOs · Policies        │
                └─────┬───────────────────┬───────────┘
                      │                   │
              ┌───────▼─────┐     ┌───────▼─────┐
              │  MongoDB 8  │     │  Valkey 9   │
              │ (write side)│     │  (cache /   │
              │ (read views)│     │   sessions) │
              └─────────────┘     └─────────────┘
```

**Patrones aplicados** (estilo _Codely / DDD-in-action_):

- **DDD táctico** — Aggregates, Value Objects, Domain Errors, Repositorios como puertos.
- **Hexagonal / Ports & Adapters** — el dominio no conoce a Mongo, ni a FastAPI.
- **CQRS-lite** — módulos `*_views` para lectura desacoplados de los aggregates de escritura.
- **Command/Query Bus** — un único punto de orquestación, ideal para _cross-cutting concerns_ (logging, métricas, transacciones).
- **Feature-Sliced Frontend** — cada feature es autocontenida (`ui/`, `services/`, `store/`, `schemas/`, `types/`).

---

## 🧰 Stack tecnológico

### Backend

`Python 3.11+` · `FastAPI` · `Pydantic v2` · `MongoDB 8` (driver síncrono **PyMongo**) · `Valkey 9` (drop-in Redis OSS) · `JWT (python-jose)` · `bcrypt` · `SlowAPI` (rate-limit) · `Poetry` · `pytest + pytest-cov` · `mongomock` · `fakeredis` · `ruff + black`.

### Frontend

`React 19` · `TypeScript 5.7` · `Vite 8` · `TailwindCSS 4` · `Radix UI` · `Zustand` (state) · `React Hook Form + Zod` (forms) · `React Router 7` · `Sonner` (toasts) · `Lucide` (icons) · `ESLint + Prettier`.

### DevEx & Plataforma

`Docker` · `Docker Compose` · `Nginx` (frontend prod) · `entrypoint.sh` (migrate + seed idempotentes) · _script unificado_ `run.py`.

---

## ⚡ Quickstart (1 comando)

> Recomendado para evaluadores. Levanta un docker compose con **MongoDB + Valkey + API + Frontend** con configuración interactiva.

```bash
python run.py
```

El script hará:

1. Crear `.env.api` y `.env.mongo` desde sus `*.example`.
2. Generar un `JWT_SECRET` seguro con `openssl`.
3. Preguntar credenciales de MongoDB y si quieres habilitar cache.
4. Asegurar el servicio `app` (frontend) en `docker-compose.yml`.
5. `docker compose up -d` y esperar `healthchecks`.

**Servicios al terminar:**

| Servicio    | URL                        |
| ----------- | -------------------------- |
| 🖥️ Frontend | http://localhost:5173      |
| 🔌 API      | http://localhost:8000      |
| 📚 Swagger  | http://localhost:8000/docs |
| 🗃️ MongoDB  | `localhost:27017`          |
| ⚡ Valkey   | `localhost:6379`           |

---

## 🛠️ Setup manual por servicio

Cada subproyecto es **independiente** y tiene su propio README detallado:

- 📘 **Backend** → [`backend/README.md`](./backend/README.md)
- 📗 **Frontend** → [`frontend/README.md`](./frontend/README.md)

> También puedes levantar la stack vía `docker compose up --build` si ya configuraste tus `.env.*`.

---

## 🗂️ Estructura del monorepo

```
miseventos/
├── backend/                    # FastAPI · DDD · CQRS-lite
│   ├── src/
│   │   ├── apps/api/           # Capa de entrega (HTTP, DI, middleware, routes)
│   │   └── modules/            # Bounded contexts
│   │       ├── auth/
│   │       ├── events/         # write side (aggregate Event)
│   │       ├── event_sessions/
│   │       ├── event_views/    # read side (CQRS)
│   │       ├── registrations/
│   │       ├── users/  · roles/  · *_views/
│   │       └── shared/         # kernel: buses, VOs, security, cache
│   ├── tests/{unit,integration}
│   ├── scripts/                # migrate.py · seed.py · entrypoint.sh
│   └── .agents/skills/         # 🤖 skills de scaffolding DDD (ver abajo)
│
├── frontend/                   # React 19 · Feature-Sliced
│   ├── src/
│   │   ├── app/                # routes, providers, shell
│   │   ├── features/           # auth · events · profile · registrations · users · shared
│   │   └── lib/
│   └── .agents/skills/         # 🤖 skills de feature/component scaffolding
│
├── docker-compose.yml          # mongo · valkey · api · app
├── run.py                      # 🚀 arranque interactivo end-to-end
└── .env.{api,mongo}.example
```

---

## 🧠 Decisiones técnicas (ADR-lite)

> ¿Por qué tomamos cada decisión? Resumen ejecutivo aquí; detalle profundo en los READMEs por servicio.

### 1. **MongoDB en lugar de PostgreSQL**

La prueba permite ambos. Elegimos Mongo porque:

- Un `Event` tiene **datos jerárquicos** (sesiones, ponentes, capacidad por sesión) → encaja con documentos.
- Lecturas dominantes con filtros parciales por `name` → índices `text` y `regex` con índices compuestos rinden excelente.
- Iteración rápida sin migraciones DDL.
- Migraciones idempotentes versionadas en `scripts/migrate.py` (mismo principio que Alembic, sin el coste de un schema rígido).

### 2. **DDD + Hexagonal + CQRS-lite**

- Separa **negocio** (invariantes de `Event`, `Capacity`, `DateRange`) de **infraestructura** (Mongo, FastAPI).
- Permite **testear el dominio sin tocar I/O** (mongomock + fakeredis).
- Los módulos `*_views` materializan proyecciones de lectura, listos para escalar a _materialized views_ o _read replicas_.
- Inspirado en repos referencia: [CodelyTV/scala-ddd-example](https://github.com/CodelyTV/scala-ddd-example), [dotnet-architecture/eShopOnContainers](https://github.com/dotnet/eShop), [heynickc/awesome-ddd](https://github.com/heynickc/awesome-ddd).

### 3. **Frontend Feature-Sliced**

Inspirado en [feature-sliced.design](https://feature-sliced.design/) y la arquitectura de Vercel/Linear. Cada _feature_ trae su `ui/`, `store/`, `services/`, `schemas/`, `types/`. Cero acoplamiento horizontal, fácil eliminar features sin romper otras.

### 4. **Valkey en lugar de Redis + sesiones auto-gestionadas**

Fork OSS bajo BSD post relicensia de Redis. Mismo protocolo, mismo cliente, futuro-proof.

Además, **las sesiones de refresh-token viven en Valkey con TTL nativo**: expiran solas sin cron jobs ni procesos de limpieza — cero mantenimiento operativo. Al hacer logout o rotación de credenciales, se borra la clave y el refresh queda **revocado instantáneamente** (stateless JWT + blacklist O(1) = lo mejor de ambos mundos). Más seguro que un JWT "puro" que sobrevive hasta su `exp` pase lo que pase.

### 5. **Command/Query Bus**

Atajo natural para cross-cutting (auth, logging, idempotencia, tracing). Permite mover handlers a workers async sin tocar las rutas.

### 6. **Roles desde el dominio**

`admin` / `organizer` / `attendee` validados a nivel de **policy** del dominio + `RequireRoles` en ruta. Nunca solo en el frontend.

---

## 🤖 Skills `.agents/` — _Agent-Native Development_

Una de las apuestas diferenciales del proyecto: ambos repos incluyen un directorio **`.agents/skills/`** con **skills reutilizables** que cualquier agente (Cascade, Claude Code, Cursor, Copilot Workspace) puede ejecutar para _scaffolding consistente con la arquitectura_.

### Backend — `backend/.agents/skills/`

| Skill                        | Genera                                                           |
| ---------------------------- | ---------------------------------------------------------------- |
| `module-scaffolding`         | Bounded context completo (domain + application + infrastructure) |
| `domain-layer`               | Aggregate root, Value Objects, errores y repository port         |
| `application-layer`          | Commands, Queries y sus handlers (CQRS)                          |
| `infrastructure-persistence` | Repos Mongo + In-Memory + view repositories                      |
| `views-module`               | Módulo de lectura CQRS (proyecciones)                            |
| `testing-unit`               | Templates de tests unitarios para handlers, services y VOs       |

### Frontend — `frontend/.agents/skills/`

| Skill                   | Genera                                            |
| ----------------------- | ------------------------------------------------- |
| `feature`               | Feature completa (ui/services/schemas/types)      |
| `component`             | Componente UI con Tailwind + Radix                |
| `lib`                   | Utilidad pura tipada                              |
| `containerized-command` | Comando reproducible dentro de Docker             |
| `project-knowledge`     | Mapa vivo del proyecto para onboarding de agentes |

> **¿Por qué importa?** Reduce la deuda arquitectónica desde día 1. Cualquier nuevo módulo nace con la **misma forma** que los existentes, lo que es crítico en equipos donde humanos y agentes colaboran. Es el equivalente a _codegen + linter de arquitectura_, llevado al ecosistema agentic.

---

## 🧪 Calidad, testing y observabilidad

- **Cobertura ≥ 80% obligatoria** (`pytest --cov-fail-under=80`).
- **Unit + Integration** tests con `mongomock` y `fakeredis` → pipeline determinista.
- **Rate limiting** por IP (SlowAPI) en endpoints sensibles.
- **Access log middleware** con `request_id` y latencias.
- **Healthchecks** Docker en los 4 servicios.
- **Exception handlers** centralizados → respuestas con `code` + `message` consistentes.
- **OpenAPI 3.1** auto-generado y _persistAuthorization_ en Swagger.

---

## 🗺️ Roadmap & próximos pasos

- [ ] Estadísticas en tiempo real.
- [ ] Métricas Prometheus + dashboards Grafana.
- [ ] OpenTelemetry tracing end-to-end.
- [ ] CI/CD con GitHub Actions (lint + tests + coverage gate + image build).
- [ ] PWA + notificaciones push para asistentes.
- [ ] i18n y accesibilidad WCAG AA.

---

<div align="center">

**Hecho con ❤️ y obsesión por los detalles.**
_Si encuentras algo que pueda mejorarse, es bienvenido — la calidad técnica es un proceso, no un estado._

</div>
