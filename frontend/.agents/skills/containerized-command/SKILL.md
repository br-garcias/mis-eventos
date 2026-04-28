---
name: containerized-command
description: Executes runtime commands (install, dev, test, build, lint, type-check) exclusively through Docker containers using the global `run_dev.sh` script. Prevents direct execution on the host and ensures environment consistency across different frontend frameworks.
license: Proprietary
compatibility: Docker, Node.js, Framework-agnostic
metadata:
  author: Hexora Team
  version: '2.0'
---

## 📁 Structure

- **Global Script**: `/usr/local/bin/run_dev.sh` (never modify this script)
- **Usage Pattern**: `run_dev.sh [OPTIONS] -i <image> -c "<command>"`

## ⚠️ CRITICAL RULES - ERROR PREVENTION

1. **NEVER run commands directly on the host**: Do NOT use `bun`, `npm`, `node`, `npx`, `yarn`, or any runtime command directly. Always use Docker.
2. **ALWAYS use the global `run_dev.sh` script**: This script is pre-installed globally. Do NOT use `./run_dev.sh` or local paths.
3. **Always use Node image**: Use `node:24` as the container image for all frontend operations.
4. **Required flags**:
   - `-i node:24`: Specifies the Node runtime image.
   - `-c "<command>"`: The command to execute inside the container.
   - `-rm`: Remove container after execution (clean up).
   - `-p <port>`: Port forwarding for dev servers.

## Step-by-Step Instructions

### For Package Installation
1. Use: `run_dev.sh -rm -i node:24 -c "yarn global add pnpm && pnpm config set store-dir /home/node/.local/share/pnpm/store && pnpm install"`
2. Verify `node_modules` or lockfiles are updated.

### For Development Server
1. Choose an available port (default: 8000).
2. Run: `run_dev.sh -rm -p <port> -i node:24 -c "<dev-command> --port <port>"`
   - **IMPORTANT**: If using **Vite**, you MUST add the `--host` flag (e.g., `yarn dev --port 8000 --host`) so the server is accessible from your browser.
3. Set `Blocking: false` for long-running processes.

### For Running Tests
1. Run: `run_dev.sh -rm -i node:24 -c "<test-command>"`
2. Report results and errors clearly.

### For Validation (TSC/Lint)
1. Type checking: `run_dev.sh -rm -i node:24 -c "<type-check-command>"`
2. Linting: `run_dev.sh -rm -i node:24 -c "<lint-command>"`

## Usage Examples

- Install package: Use Docker, never direct `npm` or `yarn`.
- Start dev server (Next.js): `run_dev.sh -rm -p 8000 -i node:24 -c "yarn dev --port 8000"`
- Start dev server (Vite): `run_dev.sh -rm -p 8000 -i node:24 -c "yarn dev --port 8000 --host"`
- Production build: `run_dev.sh -rm -i node:24 -c "yarn build"`.

## Edge Cases

- **Port in use**: Try alternative ports (8001, 8002).
- **Container failure**: Verify Docker status and command syntax.
- **Persistence**: Ensure changes to files are reflected on the host (the script handles volume mapping).
