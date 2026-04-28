---
name: application-layer
description: Guides creation of Application layer artifacts (Command/Query, CommandHandler/QueryHandler, Service, Response DTO) in either a command module or a `_views` query module.
---

## When to invoke

- The user wants to add a new use case (any command or query).
- The user is refactoring a Handler that contains business logic.
- The user needs to wire a new handler into the CommandBus or QueryBus.

## Two flavors of module

| Module form                                                | What lives here                                                                                       | Allowed dependencies                                                                                                                                                      |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `<module>` — plural noun (e.g. `users`)                    | **Commands only** — state changes. Loads aggregates by id when a command requires it.                 | Write-side `Repository` ports of its own bounded context. May call domain ports of other contexts (e.g. `RoleRepository.find_by_id`) when a command genuinely needs them. |
| `<entity>_views` — singular + `_views` (e.g. `user_views`) | **Queries only** — read-side projections. Returns Response DTOs that may join data across aggregates. | A single `<Entity>ViewRepository` port that takes filters and returns DTOs. **Never** depends on write-side repositories. See `@views-module`.                        |

> Rule of thumb: if the use case ends with persistence change → command module. If it returns a DTO and never mutates state → views module.

## Core principles (CodelyTV pattern)

1. **Handler = dumb orchestrator**: receives an already-built Service via constructor injection; `handle()` is a single delegation line.
2. **Service = business logic**: ALL validation, transformation, and persistence calls. Depends on ports, not adapters.
3. **Composition lives in `apps/<app>/di/<module>_di.py`**: only the DI module wires `Service(repo, ...)` and passes it to `Handler(service)`. Handlers know nothing about repositories or config.
4. **Response DTO**: queries return a Response, never raw domain entities.
5. **One folder per use case**: `src/modules/<module>/application/<use_case>/`.

## Folder layout per use case (command module)

Every use case is opt-in. Create only what the bounded context needs.

```
src/modules/<module>/application/<use_case>/
├── <verb>_<entity>_command.py
├── <verb>_<entity>_command_handler.py    # implements CommandHandler
└── <entity>_<doer>.py                    # business logic (Creator, Updater, ...)
```

## Folder layout per use case (`<entity>_views` query module)

```
src/modules/<entity>_views/application/<use_case>/
├── <noun>_query.py
├── <noun>_query_handler.py               # implements QueryHandler
├── <entity>_<reader>.py                  # business logic (Searcher, FinderById, ...)
└── <entity>_response.py                  # Response DTO
```

## Steps

### 1. Command or Query

Use `templates/command.py.tmpl` or `templates/query.py.tmpl`. `@dataclass(frozen=True)`, primitives only.

### 2. Service

Use `templates/service.py.tmpl`. Inject only ports the use case needs. Be explicit in `__init__`. Cross-context lookups (e.g. `RoleRepository` from a `users` command) are fine when the command genuinely depends on them.

For `_views` services: inject the `ViewRepository` port; map its rows into a `Response` DTO.

### 3. Handler

Use `templates/command_handler.py.tmpl` or `templates/query_handler.py.tmpl`. Single-line `handle()` that delegates to the service.

## Handler registration

Wire each new handler in `src/apps/<app>/di/<module>_di.py` (or `<entity>_views_di.py`). Compose the Service first, inject it into the Handler:

```python
def <module>_command_handlers():
    creator = <Entity>Creator(<entity>_repository, ...)
    return {
        Create<Entity>Command: Create<Entity>CommandHandler(creator),
    }
```

The composition root (`apps/<app>/di/__init__.py`) merges every module's maps into the buses.

## Command rules

- **ID generation**: always in API, not in domain
- **Return values**: commands return `None`, only return if strictly needed
- **Cache invalidation**: call `invalidate_all()` after every successful write

## Reference templates

- [templates/command.py.tmpl](templates/command.py.tmpl)
- [templates/query.py.tmpl](templates/query.py.tmpl)
- [templates/command_handler.py.tmpl](templates/command_handler.py.tmpl)
- [templates/query_handler.py.tmpl](templates/query_handler.py.tmpl)
- [templates/service.py.tmpl](templates/service.py.tmpl)
