---
name: lib
description: Creates pure TypeScript utility functions and modules in modular frontend applications. Use when building core utilities that are framework-agnostic, such as data transformations, validation helpers, or shared logic without dependencies.
license: Proprietary
compatibility: TypeScript, Framework-agnostic
metadata:
  author: Hexora Team
  version: '2.0'
---

## 📁 Structure

- **Destination path (Core)**: `src/lib/[util-name].ts`
- **Destination path (Feature-specific)**: `src/features/[feature-name]/utils/[util-name].ts` or `src/features/shared/utils/[util-name].ts`

## ⚠️ Rules

1. **No UI Framework Dependencies**: Utilities defined here must be agnostic (no hooks, no JSX, no UI state). They must be pure functions.
2. **Strict Typing**: All function parameters and return values must be strictly typed.
3. **Error Handling**: Define clear business exceptions or return types for failure cases.
4. **Documentation**: Use JSDoc to explain the purpose and parameters of core utilities.

## Step-by-Step Instructions

1. Determine the appropriate path: use `src/lib/` for global utilities, or feature-specific paths for localized helpers.
2. Create the `.ts` file with descriptive naming.
3. Define pure functions that perform specific transformations or calculations.
4. Use TypeScript interfaces or types for parameters and returns.
5. Add JSDoc comments to explain function purpose.
6. Export functions and types appropriately.

## Usage Examples

- Date formatting utilities used across features: `src/lib/dates.ts`.
- Business metric calculations taking plain data and returning results without side effects.
- String manipulation or validation helpers for general use.

## Edge Cases

- For utilities that might throw errors, use custom error types or descriptive messages.
- For asynchronous operations, ensure proper Promise typing and error propagation.
- If a utility grows complex, break it into smaller, focused functions.
