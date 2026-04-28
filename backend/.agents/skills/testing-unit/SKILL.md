---
name: testing-unit
description: Guides the creation of unit tests for Domain, Application services, and Handlers in any module — command-side or `_views`.
---

## When to invoke

- The user asks for tests on a new use case.
- The user wants to test domain validation (Value Objects).
- The user needs to verify a Handler delegates correctly to its Service.

## Core principles

1. **No real infrastructure**: in-memory fakes for repositories, hashers, token services, view repositories.
2. **Test the Service, not the Handler**: the Service contains the logic. The Handler is a thin adapter.
3. **Separate arrange / act / assert** clearly.
4. **`MagicMock(spec=Repository)`** when you need a strict mock that mirrors the real interface.
5. **VO tests assert `InvalidArgumentError`**, never bare `ValueError`.

## What to test by layer

| Layer                          | What                                                                    | How                                                                                      |
| ------------------------------ | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Domain VO                      | Validation rules                                                        | Direct instantiation; expect `InvalidArgumentError`.                                     |
| Domain Aggregate               | `create()` aggregates field errors; `update`/`toggle` state transitions | Direct method calls; assert on state and `DomainValidationError`.                        |
| Application Service (command)  | Happy path + error paths (NotFound / AlreadyExists / DomainValidation)  | Fakes / mocks for repositories; call the service entry point.                            |
| Application Service (`_views`) | Filter combinations, empty results, DTO shape                           | Fake `ViewRepository` returning canned rows; assert `Response` shape.                    |
| Handler                        | Delegates to its Service exactly once                                   | `MagicMock(spec=Service)`; assert `handle()` calls the right method with the right args. |

## Folder structure (mirrors `src/modules/`)

```
tests/unit/modules/<module>/
├── domain/
│   ├── test_<entity>_<vo>.py
│   └── test_<entity>.py
└── application/
    └── test_<use_case>.py        # one file per use case the module exposes

tests/unit/modules/<entity>_views/
└── application/
    └── test_<query>.py
```

> Reminder: command modules are plural (`users`), views modules are singular + `_views` (`user_views`). Tests mirror the same naming.

Add only what the module actually has. If the module exposes one command, write one application test file.

## Steps

### 1. Domain VO tests

Use `templates/test_value_object.py.tmpl`. Cover at least one valid and the relevant invalid cases.

### 2. Application Service tests

Use `templates/test_service.py.tmpl`. Use shared fakes from `tests/unit/modules/_fakes.py` (extend it when a new port appears). Assert side effects on the fake repository and the exceptions on error paths.

### 3. Handler tests

Use `templates/test_handler.py.tmpl`. Mock the Service, call `handle()`, verify delegation.

## Reference templates

- [templates/test_value_object.py.tmpl](templates/test_value_object.py.tmpl)
- [templates/test_service.py.tmpl](templates/test_service.py.tmpl)
- [templates/test_handler.py.tmpl](templates/test_handler.py.tmpl)
