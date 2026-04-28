---
name: project-knowledge
description: Defines the architecture, organization, and conventions of a modular frontend application following a business domain-oriented structure (Feature-Sliced Design). Framework-agnostic and compatible with Next.js, Vite, and others.
license: Proprietary
compatibility: Framework-agnostic (Next.js, Vite, etc.), TypeScript, Feature-Sliced Design
metadata:
  author: Hexora Team
  version: '2.0'
---

## 🏗 Project Architecture

The project follows a strict modular architecture oriented to business domains (simplified Feature-Sliced Design), designed to be **agnostic to the framework**.

- **`src/app/` or `src/pages/`**: Routing layer (framework dependent). Pages here act solely as containers/delegates.
- **`src/features/`**: Isolated business modules. Each feature represents a domain (e.g., auth, users) and contains its own UI, services, types, and schemas.
- **`src/features/shared/`**: Shared module for reusable UI components, global stores (e.g., zustand), and transversal utilities.
- **`src/lib/`**: Pure TypeScript code without UI dependencies (e.g., HTTP clients, CriteriaBuilder, formatters).

## ⚠️ Critical Rules and Conventions

1. **No custom hooks**: Logic must be maintained within components using native hooks or extracted to pure utilities in `lib/` or feature-specific utils.
2. **Feature Isolation**: A feature (`src/features/A`) MUST NOT import code from another feature (`src/features/B`). Any code that needs to be shared must be moved to `src/features/shared`.
3. **Delegated Pages**: Route entry points should only import and render the corresponding feature UI component. They should not contain business logic or data fetching.
4. **Data Fetching**: Performed via the `services/` layer in features, using `lib/` utilities. Loading states and errors must be handled explicitly in feature components.
5. **Agnostic Logic**: The core business logic and structure must remain identical regardless of whether Next.js or Vite is used.

## 🛠 Available Skills

This project defines the following skills for specific tasks:

- **feature**: Creates the complete structure for a new business module.
- **component**: Creates reusable UI components following strict conventions.
- **lib**: Creates pure TypeScript utility functions and modules.
- **project-knowledge**: This skill, providing architectural context.
- **containerized-command**: Executes runtime commands exclusively through Docker.

## Usage Examples

- Always invoke this skill at the start of a task to understand the project structure.
- Review these conventions before creating or modifying features.
- Ensure all imports follow the isolation rules to avoid circular dependencies.

## Edge Cases

- If a shared utility is feature-specific, move it to `src/features/shared/utils/` instead of `lib/`.
- For global state management, use `src/features/shared/` stores.
- The `src/app/` or `src/pages/` structure depends on the framework in use, but the delegation principle remains.
