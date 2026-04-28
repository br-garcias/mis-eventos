---
name: feature
description: Creates the complete structure for a new business module (feature) in modular frontend applications. Use when implementing new business domains with isolated UI, services, types, and schemas.
license: Proprietary
compatibility: Framework-agnostic, TypeScript, Feature-Sliced Design, Zod
metadata:
  author: Hexora Team
  version: '2.0'
---

## 📁 Structure

- **Destination path**: `src/features/[feature-name]/`
- **Internal Organization**:
  - `types/index.ts`: Data interfaces and API DTOs.
  - `schemas/index.ts`: Validation schemas (Zod) for forms and data.
  - `services/index.ts`: API integration (get, create, update, delete) using `CriteriaBuilder` (from `lib/`).
  - `ui/`: Feature-specific UI components (Page, Table, Form, Filters, etc.).

## ⚠️ Rules

1. **Runtime Operations**: ALWAYS use the `containerized-command` skill for any runtime operations. Never run runtime commands directly on the host.
2. **No Custom Hooks**: Maintain state logic within components using native hooks or pure utilities.
3. **Isolated Feature**: A feature MUST NOT import nor depend on other features. Shared components must come from `src/features/shared/`.
4. **Data Handling**: Fetching listings must use `CriteriaBuilder` for standardized pagination, ordering, and filtering.

## Step-by-Step Instructions

1. Create the feature directory structure under `src/features/[feature-name]/`.
2. Define data types and interfaces in `types/index.ts`.
3. Create validation schemas in `schemas/index.ts` using Zod.
4. Implement the API service layer in `services/index.ts`.
5. Build UI components in the `ui/` directory.
6. Ensure the main orchestrator component is named `[FeatureName]Page.tsx` (or similar depending on routing).

## Usage Examples

- When adding a new section like "User Management", create a new feature for it.
- For CRUD operations, structure the feature with list, create, edit, and delete components.
- Use shared components from `src/features/shared/ui/` for common elements.

## Edge Cases

- If a feature grows too large, consider splitting it into sub-features or moving shared logic to `shared`.
- For global state, integrate with shared stores in `src/features/shared/`.
- Ensure proper error boundaries and loading states are implemented in the main feature components.
