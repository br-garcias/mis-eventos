---
name: infrastructure-persistence
description: Guides the implementation of write-side repositories (InMemory + Mongo) for command modules and read-side ViewRepositories for `_views` modules.
---

## When to invoke

- The user asks to implement a new persistence adapter.
- The user wants to add MongoDB support to an existing module.
- The user is creating a `_views` module and needs a `ViewRepository`.

## Two adapter families

| Used in                                                            | Port                                      | Purpose                                                                                                                                        |
| ------------------------------------------------------------------ | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `<module>/infrastructure/persistence/` (plural module)             | `<entity>_repository.py` (write-side)     | Persist + reload a single aggregate. **No joins.**                                                                                             |
| `<entity>_views/infrastructure/persistence/` (singular + `_views`) | `<entity>_view_repository.py` (read-side) | Read-only queries that may join across collections (`$lookup`, aggregation pipelines, denormalized views). Returns DTOs, **never** aggregates. |

> Naming reminder: the command module is plural (`users`), the views module is the **singular** entity + `_views` (`user_views`).

## File layout

```
src/modules/<module>/infrastructure/persistence/        # e.g. users/infrastructure/persistence/
├── in_memory_<entity>_repository.py                    # tests / dev only
└── mongo_<entity>_repository.py                        # production

src/modules/<entity>_views/infrastructure/persistence/  # e.g. user_views/infrastructure/persistence/
├── in_memory_<entity>_view_repository.py               # optional, for tests
└── mongo_<entity>_view_repository.py                   # production read model
```

## Steps

### 1. InMemory write-side repository

Use `templates/in_memory_repository.py.tmpl`. Implements every method of the domain port. Useful for unit tests and local dev.

### 2. Mongo write-side repository

Use `templates/mongo_repository.py.tmpl`. Lives in `<module>/infrastructure/persistence/`. Inherits both the domain port and the shared `MongoRepository` base.

- `to_document` reads `.value` from VOs (`id.value`, `name.value`, `is_active.value`).
- `from_document` calls the domain factory `<Entity>.create(...)` so grouped validation runs. Never construct the aggregate with raw VOs.
- One collection per aggregate.

### 3. Mongo view repository (`<entity>_views` module)

Use `templates/mongo_view_repository.py.tmpl`. Lives in `<entity>_views/infrastructure/persistence/` (singular form). Inherits the view port and the shared `MongoRepository` base.

- May read from any number of collections via aggregation (`$lookup`) — joins are explicitly allowed here, **not** in write-side repos.
- Returns plain `dict`s or DTOs the application service maps into a `Response`.
- No aggregate factory calls; the read model can be denormalized.

### 4. Shared `MongoRepository` base

Already at `src/modules/shared/infrastructure/persistence/mongo/mongo_repository.py`. Provides `_collection()` and `_persist(id, document)`.

### 5. Wire into DI

Edit `src/apps/<app>/di/<module>_di.py` (write side, plural) or `<entity>_views_di.py` (read side, singular):

```python
<Entity>_repository = Mongo<Entity>Repository(MongoClientFactory(), mongo_config)
```

## Reference templates

- [templates/in_memory_repository.py.tmpl](templates/in_memory_repository.py.tmpl)
- [templates/mongo_repository.py.tmpl](templates/mongo_repository.py.tmpl)
- [templates/mongo_view_repository.py.tmpl](templates/mongo_view_repository.py.tmpl)
