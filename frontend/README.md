<div align="center">

# 🖥️ Mis Eventos — Frontend

**SPA moderna en React 19 + TypeScript con arquitectura _Feature-Sliced_, Tailwind v4 y Radix UI.**

[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind](https://img.shields.io/badge/Tailwind-4-38BDF8?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Zustand](https://img.shields.io/badge/Zustand-5-FFB000)](https://zustand-demo.pmnd.rs/)
[![Zod](https://img.shields.io/badge/Zod-4-3E67B1?logo=zod&logoColor=white)](https://zod.dev/)
[![pnpm](https://img.shields.io/badge/pnpm-recomendado-F69220?logo=pnpm&logoColor=white)](https://pnpm.io/)

</div>

---

## 📖 Tabla de contenido

- [Visión general](#-visión-general)
- [Características](#-características)
- [Stack técnico](#-stack-técnico)
- [Arquitectura Feature-Sliced](#-arquitectura-feature-sliced)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Rutas y guards](#-rutas-y-guards)
- [Gestión de estado](#-gestión-de-estado)
- [Configuración (variables de entorno)](#-configuración-variables-de-entorno)
- [Ejecución local](#-ejecución-local)
- [Ejecución con Docker](#-ejecución-con-docker)
- [Build de producción](#-build-de-producción)
- [Lint, format & type-check](#-lint-format--type-check)
- [Performance & UX](#-performance--ux)
- [Skills `.agents/` para scaffolding de features](#-skills-agents-para-scaffolding-de-features)
- [Decisiones técnicas](#-decisiones-técnicas)

---

## 🎯 Visión general

Frontend de la plataforma **Mis Eventos**: listado y detalle de eventos, creación/edición (organizadores y admin), inscripción de asistentes, perfil con eventos registrados, autenticación (login/registro/refresh), administración de usuarios.

Diseñado con foco en **DX**, **UX**, **performance** y **arquitectura escalable** (estilo _Feature-Sliced Design_, similar a las bases de Linear, Vercel y Cal.com).

## ✨ Características

- 🧱 **Arquitectura por _features_** autocontenidas (`ui/`, `services/`, `store/`, `schemas/`, `types/`).
- 🔐 **Auth flow completo** — login, registro, refresh transparente con interceptores, _route guards_ (`RequireAuth`, `RedirectIfAuth`, RBAC por roles).
- 🛣️ **Routing** declarativo con `react-router-dom` v7 + **`React.lazy`** por página → bundle splitting automático.
- 🧠 **State management** con **Zustand** + persistencia selectiva (token, perfil) en cookies seguras.
- 📝 **Formularios** con **React Hook Form + Zod** → validación tipada compartida con el backend.
- 🎨 **Tailwind v4 + Radix UI** → componentes accesibles (a11y) y un design system propio en `features/shared/ui/`.
- 🦴 **Skeletons + Spinners** por página y feature → percepción inmediata de carga.
- 🍞 **Toasts** con `sonner` para feedback de acciones.
- 🐳 **Docker multi-stage** (`node` → `nginx`) optimizado para producción.
- ✅ **TypeScript estricto** con `tsc --noEmit` en el pipeline.

---

## 🧰 Stack técnico

| Área        | Librerías                                                                         |
| ----------- | --------------------------------------------------------------------------------- |
| Core        | React 19, TypeScript 5.7, Vite 8                                                  |
| Estilos     | TailwindCSS 4 (`@tailwindcss/vite`), `tailwind-merge`, `class-variance-authority` |
| UI          | Radix UI primitives, Lucide icons, Sonner                                         |
| Routing     | `react-router-dom` 7                                                              |
| Estado      | Zustand 5                                                                         |
| Formularios | React Hook Form 7 + Zod 4 + `@hookform/resolvers`                                 |
| HTTP        | `fetch` nativo encapsulado (`features/shared/services/`)                          |
| Auth client | `js-cookie`                                                                       |
| Calidad     | ESLint 10, Prettier, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`   |

---

## 🏛️ Arquitectura Feature-Sliced

Cada **feature** es una mini-app autocontenida. Las dependencias fluyen hacia abajo (`features/<x>` → `features/shared` → `lib`). Nunca de forma horizontal entre features.

```
src/
├── app/                    # composición global: providers, router, shell
│   ├── App.tsx
│   ├── main.tsx
│   └── routes.tsx
├── features/
│   ├── auth/               # login, register, guards, refresh
│   ├── events/             # listado, detalle, crear, editar
│   ├── registrations/      # inscripción + mis eventos
│   ├── profile/            # vista de perfil
│   ├── users/              # admin de usuarios (admin)
│   └── shared/             # design system + servicios + stores transversales
│       ├── ui/             # Button, Input, Modal, Card, Spinner, Skeleton, ...
│       ├── layout/         # Header, Footer, Shell
│       ├── services/       # http client, error mapper
│       ├── stores/         # auth store, ui store
│       ├── hooks/  ├── utils/  ├── constants/  ├── types/
├── lib/                    # utilidades puras, sin React
└── styles/                 # tailwind entry
```

### Anatomía de una feature

```
features/events/
├── ui/                # páginas + componentes específicos (EventCard, EventForm, ...)
│   └── skeletons/
├── services/          # llamadas HTTP a /events
├── store/             # estado local de la feature (Zustand slice)
├── schemas/           # Zod schemas compartidos UI ↔ services
└── types/             # tipos derivados de los schemas
```

---

## 📁 Estructura del proyecto

```
frontend/
├── src/
│   ├── app/                  # bootstrap React + router
│   ├── features/             # (ver arriba)
│   ├── lib/                  # helpers puros tipados
│   └── styles/
├── public/
├── .agents/skills/           # 🤖 skills de feature/component scaffolding
├── Dockerfile                # multi-stage: node-build → nginx
├── nginx.conf                # SPA fallback + caché de assets
├── vite.config.ts            # alias @ + plugin tailwind + react
├── eslint.config.js          # flat config v10
├── tsconfig.json             # paths "@/*"
└── package.json
```

---

## 🛣️ Rutas y guards

Definidas en `src/app/routes.tsx`. Todas las páginas se cargan con `React.lazy` y `Suspense` con _skeleton_ específico de la página.

| Ruta                  | Acceso               | Skeleton             |
| --------------------- | -------------------- | -------------------- |
| `/`                   | Público              | `PageLoader`         |
| `/eventos/:id`        | Público              | `PageLoader`         |
| `/eventos/crear`      | Auth requerido       | `PageLoader`         |
| `/eventos/:id/editar` | `admin`, `organizer` | `PageLoader`         |
| `/perfil`             | Auth requerido       | `ProfileSkeleton`    |
| `/login`              | Sólo invitados       | `LoginSkeleton`      |
| `/registro`           | Sólo invitados       | `RegisterSkeleton`   |
| `/admin/users`        | `admin`              | `AdminUsersSkeleton` |
| `/403`                | Público              | —                    |
| `*`                   | Público              | `NotFound`           |

`RequireAuth` y `RedirectIfAuth` viven en `features/auth/ui/RequireAuth.tsx`.

---

## 🧠 Gestión de estado

- **Zustand** por dominio: `authStore`, `uiStore`, slices por feature.
- **Persistencia** mínima (token, perfil) en cookies con `js-cookie` — más seguro que `localStorage` cuando se combina con flags `Secure` y `SameSite`.
- **Estado del servidor** modelado como _fetch + reducer_ en cada feature (sin React Query para mantener footprint pequeño; arquitectura lista para introducirlo si crece).

---

## ⚙️ Configuración (variables de entorno)

```bash
cp .env.example .env
```

| Variable       | Default                        | Descripción         |
| -------------- | ------------------------------ | ------------------- |
| `VITE_API_URL` | `http://localhost:8000/api/v1` | Base URL de la API. |

> Vite expone únicamente las variables prefijadas con `VITE_` al cliente.

---

## 🚀 Ejecución local

> Requisitos: Node 20+, `pnpm` (recomendado) o `npm`.

```bash
pnpm install
pnpm dev          # http://localhost:5173
```

La API debe estar accesible en `VITE_API_URL`. Si no la tienes corriendo, lanza la stack completa con:

```bash
# desde la raíz del repo
python run.py
```

---

## 🐳 Ejecución con Docker

```bash
# desde la raíz del repo
docker compose up --build app
```

El `Dockerfile` es multi-stage:

1. **builder (node):** `pnpm install` + `vite build`.
2. **runtime (nginx):** sirve `dist/` con fallback SPA y cache headers para assets.

`VITE_API_URL` se inyecta en build-time como `ARG`.

---

## 📦 Build de producción

```bash
pnpm build           # genera dist/
pnpm preview         # sirve localmente el build
```

Optimizaciones aplicadas por Vite:

- Tree-shaking + minificación (esbuild).
- Code-splitting por ruta (`React.lazy`).
- Hashing de assets para cache eficiente.
- Compresión Brotli/Gzip en Nginx.

---

## 🧹 Lint, format & type-check

```bash
pnpm lint            # ESLint flat config
pnpm type-check      # tsc --noEmit
pnpm format:check    # Prettier (chequeo)
pnpm format:write    # Prettier (autofix)
```

ESLint corre con `react-hooks` y `react-refresh`. Prettier alineado con el `.prettierrc` del proyecto.

---

## ⚡ Performance & UX

- **Code splitting por ruta** (todas las páginas son `lazy`).
- **Skeleton dedicado** por página crítica → mejor _perceived performance_.
- **Imágenes** servidas optimizadas; soporte para `loading="lazy"`.
- **Tailwind v4 JIT** → CSS final mínimo y purgado.
- **Radix UI** → accesibilidad WAI-ARIA out of the box (focus traps, keyboard nav).
- **Toasts** con `sonner` para feedback inmediato sin bloquear UI.
- **Error boundaries** en `app/` para fallos no manejados.
- **Estados de carga, error y vacío** explícitos en cada feature.

---

## 🤖 Skills `.agents/` para scaffolding de features

`frontend/.agents/skills/` reúne skills declarativas que cualquier agente AI (Cascade, Claude Code, Cursor) puede ejecutar para mantener la consistencia arquitectónica.

| Skill                   | Genera                                                 |
| ----------------------- | ------------------------------------------------------ |
| `feature`               | Feature completa (ui/services/schemas/types)           |
| `component`             | Componente UI con Tailwind + Radix + variantes (`cva`) |
| `lib`                   | Utilidad pura tipada con su test                       |
| `containerized-command` | Comando reproducible dentro de Docker                  |
| `project-knowledge`     | Mapa vivo del proyecto para onboarding de agentes      |

> **Por qué importa:** cualquier nueva feature/componente nace alineada con la arquitectura. Es la diferencia entre un repo _agent-friendly_ y uno donde cada PR genera deuda. Tendencia consolidada en repos top de 2025 (Anthropic, Vercel, Sourcegraph).

---

## 🧠 Decisiones técnicas

### Feature-Sliced en lugar de _atomic design_ puro

Atomic design organiza por **forma** (átomos/moléculas/organismos). Feature-Sliced organiza por **dominio** — coincide con cómo se piden los cambios en producto y hace que eliminar/migrar features sea trivial. Inspirado en [feature-sliced.design](https://feature-sliced.design/).

### Zustand en lugar de Redux/Context

- API minimalista, sin boilerplate.
- Selectores con _shallow equality_ → menos re-renders.
- Middleware de persistencia cuando hace falta.
- Footprint < 1KB.

### React Hook Form + Zod

- RHF: performance (uncontrolled) y DX excelente.
- Zod: schema único compartido con el backend → tipos derivados (`z.infer`).
- `@hookform/resolvers` une ambos sin overhead.

### Sin React Query (todavía)

Mantenemos el bundle pequeño. La capa `services/` está diseñada para envolverse con React Query/SWR cuando el caching invalidaciones lo justifique. Cero refactor mayor previsto.

### Cookies vs localStorage para auth

Cookies con `Secure + SameSite=Lax` son más resistentes a XSS que `localStorage`. El refresh transparente vive en el cliente HTTP de `features/shared/services/`.

### Tailwind v4 + Radix

- Tailwind v4: nuevo engine, configuración cero, build instantáneo.
- Radix: primitives accesibles, sin estilos opinados — combinan perfectamente con Tailwind.
- `class-variance-authority` para variantes tipadas (estilo shadcn/ui).

### TypeScript estricto + ESLint flat config v10

Garantiza calidad desde el editor. `tsc --noEmit` separado del build evita falsos negativos de Vite/SWC.

---

<div align="center">

📘 Volver al [README raíz](../README.md) · 🔌 Ver [Backend README](../backend/README.md)

</div>
