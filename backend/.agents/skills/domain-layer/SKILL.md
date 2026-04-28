---
name: domain-layer
description: Guides the correct creation of Domain layer artifacts in any Hexagonal/DDD bounded context — Value Objects, AggregateRoots, Domain Errors, and write-side Repository ports.
---

## When to invoke

- The user asks to create or modify a domain concept (Entity, VO, Error, Repository).
- The user is adding fields to an existing AggregateRoot.
- The user needs to define a write-side abstract Repository port.

> **Scope**: this skill is for **command-side modules** (plural folder name, e.g. `users`). Read-side projections that join data across aggregates belong in a sibling **singular** `<entity>_views` module (e.g. `user_views`) — see `@views-module`.

## Core principles

1. **Inherit shared bases**: VOs extend `StringValueObject`, `IdValueObject`, `BoolValueObject`, `NumberValueObject`, or `DateValueObject` from `shared.domain.value_object`. Do **not** add `@dataclass(frozen=True)` or `__slots__` manually.
2. **Validation inside VOs**: never allow invalid state to leave the constructor. The base `ValueObject.__init__` calls `_ensure_valid()` automatically. Raise `InvalidArgumentError` (from `shared.domain.value_object`) — never bare `ValueError`.
3. **Grouped validation at AggregateRoot level**: `create()` and `update()` collect ALL field errors before raising a single `DomainValidationError(errors: dict[str, list[str]])`. Use a private `_build_value_objects()` helper to iterate over candidate fields.
4. **Primitives-only public API**: `create()`, `update()`, and domain methods accept primitives (`str`, `bool`, `int`). Internally they build VOs. Never expose VO constructors outside the domain.
5. **No cross-aggregate references**: an aggregate stores at most a foreign id (e.g. `role_id`), never another aggregate's data. Cross-aggregate reads are the job of an `<entity>_views` module.
6. **No infrastructure leaks**: domain knows NOTHING about DBs, HTTP, frameworks.
7. **Python 3.11+ syntax**: use `X | None` instead of `Optional[X]`.

## Folder structure (per command module)

Every file is **on demand**. Create only what the bounded context actually needs.

```
src/modules/<module>/domain/
├── <entity>.py                    # AggregateRoot (required)
├── <entity>_<vo>.py               # one file per business-specific VO
├── <entity>_repository.py         # write-side abstract port (ABC)
├── <entity>_not_found_error.py    # only if any command needs to signal absence
└── <entity>_already_exists_error.py  # only if domain enforces uniqueness
```

## Steps

### 1. Value Object — only when business rules differ from shared VOs

Use `templates/value_object.py.tmpl`. If the value matches a shared VO (id, bool, number, date) reuse the shared one directly inside the aggregate.

### 2. AggregateRoot

Use `templates/aggregate_root.py.tmpl`. Must extend `AggregateRoot` and expose:

- `create(*, ...)` factory — collects errors, raises `DomainValidationError`.
- Domain methods that mutate state (`update`, `toggle`, ...). Add only what the use cases require.

Rules:

- Keyword-only arguments in `create()`.
- Use `BoolValueObject` for booleans, never raw `bool`.
- Never add `from_primitives()` / `to_primitives()` here — mapping belongs in the infrastructure mapper.

### 3. Repository interface (write-side)

Use `templates/repository.py.tmpl`. ABC with the operations the **commands** actually need:

- `save(entity)` — almost always.
- `find_by_id(id)` / `find_by_<unique_field>(value)` — only when a command needs to load the aggregate.
- `delete(id)` — only when a command deletes.

> Do **not** add `search_all()`, list queries, or DTO-returning methods to the write-side port. Those belong to the corresponding `<entity>_views` module.

### 4. Domain Error

Use `templates/domain_error.py.tmpl`. Plain `Exception` subclass with a descriptive message. `InvalidArgumentError` is for VO-level violations; domain-level errors (NotFound, AlreadyExists, etc.) are their own classes.

## Reference templates

- [templates/value_object.py.tmpl](templates/value_object.py.tmpl)
- [templates/aggregate_root.py.tmpl](templates/aggregate_root.py.tmpl)
- [templates/repository.py.tmpl](templates/repository.py.tmpl)
- [templates/domain_error.py.tmpl](templates/domain_error.py.tmpl)
