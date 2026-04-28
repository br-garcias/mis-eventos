---
name: module-scaffolding
description: Scaffolds a bounded-context module (command-side or `_views` read-side) with only the layers and use cases the user actually requests.
---

## When to invoke

- The user asks to create a new module.
- The user wants the folder tree for a new bounded context.

## Module flavors

| Convention                             | What it owns                                                               | When to use                                                   |
| -------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `<module>` (plural)                    | Command-side: aggregate, write-side repository, command use cases.         | Any context that mutates state.                               |
| `<entity>_views` (singular + `_views`) | Read-side: view repository (allows joins), query use cases, response DTOs. | When clients need to read data, especially across aggregates. |

> A bounded context can have **only** the command module, **only** the `_views` module, or both. They are decoupled: the views module reads the same database (or a projection of it) but does not depend on the command module's domain code.

## Naming convention

| Concept                  | Form                               | Examples                                    |
| ------------------------ | ---------------------------------- | ------------------------------------------- |
| Command module folder    | plural snake_case                  | `users`, `roles`, `sessions`                |
| Views module folder      | **singular** snake_case + `_views` | `user_views`, `role_views`, `session_views` |
| `<entity>` (file stems)  | singular snake_case                | `user`, `role`, `session`                   |
| `<Entity>` (class names) | PascalCase                         | `User`, `Role`, `Session`                   |

> The pluralization flips between the two flavors on purpose: command modules talk about _the collection of aggregates_ (`users`), while a views module is a read-model centred on _one entity perspective_ (`user_views`). If a context needs multiple unrelated read models, create one `_views` module per perspective (e.g. `user_views`, `user_audit_views`).

## Process

### Command module (`<module>`)

1. Ask the user which **commands** the bounded context exposes (Create / Update / Toggle / Delete / etc.). Don't assume a default CRUD set.
2. Invoke `@domain-layer` to create only the VOs, AggregateRoot, errors, and repository methods the listed commands actually need.
3. Invoke `@application-layer` to create one `<use_case>/` folder per command.
4. Invoke `@infrastructure-persistence` to add write-side repositories (Mongo + optional InMemory).
5. Invoke `@testing-unit` for domain + service tests.
6. Wire the handlers in `src/apps/<app>/di/<module>_di.py`.

### Views module (`<entity>_views`)

1. Invoke `@views-module` for layout, ViewRepository contract, and DTO shaping.
2. Ask the user which **queries** the read side exposes (Search / FindById / specialized projections / etc.).
3. Invoke `@application-layer` for query handlers + Response DTOs.
4. Invoke `@infrastructure-persistence` for the Mongo view repository.
5. Invoke `@testing-unit` for view repository contract tests.
6. Wire the query handlers in `src/apps/<app>/di/<entity>_views_di.py`.

## Anti-patterns to avoid

- ❌ Adding `search_all` / list / FindById queries to a command module's repository.
- ❌ Letting a `_views` service mutate state.
- ❌ Importing aggregates from `<module>` inside `<entity>_views`. The views module sees the database, not the domain.
- ❌ Scaffolding use cases the user did not request "just in case".

## Reference

- [templates/scaffold_checklist.md](templates/scaffold_checklist.md)
