---
name: component
description: Creates reusable UI components following strict conventions in modular frontend applications. Use when building UI elements for features or shared layers, ensuring they are composable and follow isolation principles.
license: Proprietary
compatibility: Framework-agnostic, TypeScript, TailwindCSS, Feature-Sliced Design
metadata:
  author: Hexora Team
  version: '2.0'
---

## 📁 Structure

- **Destination path (Feature-specific)**: `src/features/[feature-name]/ui/[ComponentName].tsx`
- **Destination path (Reusable)**: `src/features/shared/ui/[ComponentName].tsx`

## ⚠️ Rules

1. **No Custom Hooks**: Handle logic within components using native hooks or pure TypeScript utilities.
2. **Styling**: Use Tailwind CSS for consistent styling across the application.
3. **Props**: Clearly define the Props interface, prioritizing standard HTML attributes when appropriate.
4. **Composition**: Prioritize small, focused components over monolithic structures.

## Step-by-Step Instructions

1. Determine the appropriate path based on component scope (feature-specific or shared).
2. Create the component file with PascalCase naming.
3. Define the Props interface extending relevant standard types.
4. Implement the component using functional syntax.
5. Use TailwindCSS for styling and layout.
6. Handle props destructuring and provide default values.
7. Export the component for use in features or routes.

## Usage Examples

- For a button used across multiple features, place it in `src/features/shared/ui/Button.tsx`.
- When creating a form input, ensure it extends standard input attributes for compatibility.
- For complex views, break them into smaller sub-components within the same feature.

## Edge Cases

- If a component requires specific framework features, ensure they are abstracted or handled at the routing level.
- Ensure accessibility with proper ARIA attributes and semantic HTML.
- For components with many props, group related ones to maintain readability.
