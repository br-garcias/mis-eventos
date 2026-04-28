# Scaffolding checklist

Use one section per module being scaffolded. Tick only the items the user explicitly requested — do **not** pre-create unused use cases.

## Command module — `<module>`

### Domain (only what the listed commands require)

- [ ] `<entity>.py` — AggregateRoot with the methods needed (`create`, plus mutators per command).
- [ ] `<entity>_<vo>.py` — one file per business-specific VO.
- [ ] `<entity>_repository.py` — write-side ABC. Include only the methods the commands call.
- [ ] `<entity>_not_found_error.py` — if any command loads-by-id.
- [ ] `<entity>_already_exists_error.py` — if uniqueness is a domain rule.

### Application — one folder per command

For each command the user asked for:

- [ ] `<verb>_<entity>_command.py`
- [ ] `<entity>_<doer>.py` (Creator, Updater, Toggler, …)
- [ ] `<verb>_<entity>_command_handler.py`

### Infrastructure

- [ ] `mongo_<entity>_repository.py` — production write side.
- [ ] `in_memory_<entity>_repository.py` — optional, for tests.

### Tests

- [ ] Domain VO tests (one per business-specific VO).
- [ ] AggregateRoot tests for each domain method exposed.
- [ ] Service tests for each command (happy path + error paths).

### DI / Wiring

- [ ] `apps/<app>/di/<module>_di.py` exposes `<module>_command_handlers()` returning `{Command: Handler}`.
- [ ] Composition root merges it into the `CommandBus`.

---

## Views module — `<entity>_views` (singular + `_views`, e.g. `user_views`)

### Application — one folder per query

For each query the user asked for:

- [ ] `<noun>_query.py`
- [ ] `<entity>_<reader>.py` (Searcher, FinderById, …)
- [ ] `<entity>_response.py` (Response DTO)
- [ ] `<noun>_query_handler.py`

### Infrastructure

- [ ] `<entity>_view_repository.py` — read-side ABC (in `domain/` of the views module, or directly in `application/` if you keep views infrastructure-first).
- [ ] `mongo_<entity>_view_repository.py` — joins / aggregations allowed.
- [ ] `in_memory_<entity>_view_repository.py` — optional, for tests.

### Tests

- [ ] Service tests per query (filter combinations, empty results, mapping shape).

### DI / Wiring

- [ ] `apps/<app>/di/<entity>_views_di.py` exposes `<entity>_views_query_handlers()` returning `{Query: Handler}`.
- [ ] Composition root merges it into the `QueryBus`.
