---
name: views-module
description: Guides the creation of `<entity>_views` read-side modules (CQRS-lite, singular form, e.g. `user_views`) where ViewRepositories are allowed to join data across aggregates and return DTOs.
---

## When to invoke

- The user asks for a list/search/detail endpoint that needs data from more than one aggregate.
- The user wants to expose a read model decoupled from the write side.
- The user creates any module whose name ends with `_views` (always **singular** + `_views`, e.g. `users` → `user_views`).

## Why a separate module

Aggregates in the command side hold no references to other aggregates' data — only foreign ids. Forcing the write side to expose joined reads would either:

- pollute domain repositories with DTOs and joins, or
- force the application layer to orchestrate N round-trips per request.

The `_views` module sidesteps both: it reads the same database (or a projection of it) through a dedicated `ViewRepository` that **may** use `$lookup`, aggregation pipelines, denormalized collections or even a different store.

## Hard rules

1. ❌ The views module **never** mutates state.
2. ❌ The views module **never** imports aggregates / domain ports from the command-side module. It sees the database, not the domain.
3. ✅ The views module **may** join across collections.
4. ✅ The views module returns plain DTOs (`Response`), never aggregates.
5. ✅ Each query is its own use case folder, mirroring the command-side layout.

## Naming

The folder is **singular `<entity>` + `_views`**. The command-side counterpart, if it exists, stays **plural** (`<module>`).

| Command module | Views module    |
| -------------- | --------------- |
| `users`        | `user_views`    |
| `roles`        | `role_views`    |
| `sessions`     | `session_views` |

## Folder structure

```
src/modules/<entity>_views/
├── domain/
│   ├── <entity>_view_dto.py              # DTOs: RoleView, SessionView, SummaryView, DetailView
│   └── <entity>_view_repository.py       # ABC: filter inputs → DTO outputs + invalidate_cache()
├── application/
│   └── <use_case>/
│       ├── <noun>_query.py
│       ├── <noun>_query_handler.py
│       └── <entity>_<reader>.py          # service: validates filters, calls the repo
└── infrastructure/
    └── persistence/
        ├── <entity>_view_repository.py           # mongo implementation
        └── cached_<entity>_view_repository.py    # cache wrapper
```

## DTOs in domain

All DTOs (`RoleView`, `SessionView`, `SummaryView`, `DetailView`) live in `domain/<entity>_view_dto.py`. They must have:

- `to_primitive()` — convert to dict for caching
- `from_primitive(dict)` — reconstruct from cache

```python
# domain/user_view_dto.py
@dataclass(frozen=True)
class RoleView:
    id: str
    name: str

    def to_primitive(self) -> dict: return {"id": self.id, "name": self.name}

    @classmethod
    def from_primitive(cls, d: dict) -> "RoleView":
        return cls(id=d["id"], name=d["name"])
```

## Designing the ViewRepository port

Keep the contract intent-revealing — one method per read use case, not generic CRUD:

```python
class UserViewRepository(ABC):
    @abstractmethod
    def search(self, *, email: str | None = None, role_id: str | None = None) -> list[UserSummaryView]: ...

    @abstractmethod
    def find_by_id(self, id: str) -> UserDetailView | None: ...

    @abstractmethod
    def invalidate_cache(self) -> None: ...
```

**Important**: The port includes `invalidate_cache()` for cache invalidation. The implementation handles the actual cache logic.

## Caching pattern

The `Cached<Entity>ViewRepository` wraps the mongo repository and handles caching automatically:

```python
# infrastructure/persistence/cached_user_view_repository.py
class CachedUserViewRepository(UserViewRepository):
    def __init__(self, inner: UserViewRepository, cache: Cache, ttl_seconds: int = 60):
        self._inner = inner
        self._cache = cache
        self._ttl = ttl_seconds

    def search(self, *, email: str | None = None, role_id: str | None = None) -> list[UserSummaryView]:
        key = f"users:search:email={email}:role={role_id}"
        cached = self._cache.get(key)
        if cached is not None:
            return [UserSummaryView.from_primitive(item) for item in cached]

        result = self._inner.search(email=email, role_id=role_id)
        self._cache.set(key, [item.to_primitive() for item in result], ttl_seconds=self._ttl)
        return result

    def invalidate_cache(self) -> None:
        self._cache.invalidate_prefix("users:")
```

**Flow**: cache.get() → HIT returns cached | MISS → inner.search() → cache.set() → returns result

## Application service

The service receives only the repository (which already includes caching):

```python
# application/search/user_searcher.py
class UserSearcher:
    def __init__(self, view_repository: UserViewRepository):
        self._view_repository = view_repository

    def run(self, *, email: str | None = None, role_id: str | None = None) -> list[UserSummaryView]:
        return self._view_repository.search(email=email, role_id=role_id)
```

## Mongo view repository

- Build the aggregation pipeline inside the adapter.
- Use `$lookup` for cross-collection joins explicitly.
- Project only the fields the DTO needs.
- Import DTOs from `domain/<entity>_view_dto.py`.

## DI wiring

Per app:

```python
# apps/<app>/di/<entity>_views_di.py
mongo_repo = Mongo<Entity>ViewRepository(MongoClientFactory(), mongo_config)
cached_repo = Cached<Entity>ViewRepository(mongo_repo, redis_cache, ttl_seconds=60)

def <entity>_views_query_handlers():
    searcher = <Entity>Searcher(cached_repo)
    return {
        Search<Entity>sQuery: Search<Entity>sQueryHandler(searcher),
    }
```

The composition root merges the returned map into the `QueryBus`.

## Tests

- Service tests use a fake `ViewRepository` returning canned rows.
- Optional contract tests for the Mongo adapter against `mongomock` to validate the aggregation shape.

## See also

- `@domain-layer` — for the command-side rules this module deliberately avoids.
- `@application-layer` — for the generic Query / Handler / Service / Response pattern.
- `@infrastructure-persistence` — for the Mongo view repository template.
