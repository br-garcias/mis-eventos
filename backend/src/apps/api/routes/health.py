from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    from apps.api.di.cache_di import cache
    from apps.api.di.shared_di import mongo_client
    from modules.shared.infrastructure.cache.valkey_cache import ValkeyCache

    components: dict[str, str] = {"api": "ok"}
    try:
        mongo_client.admin.command("ping")
        components["mongo"] = "ok"
    except Exception as exc:  # noqa: BLE001
        components["mongo"] = f"down: {exc}"

    if isinstance(cache, ValkeyCache):
        components["valkey"] = "ok" if cache.ping() else "down"
    else:
        components["valkey"] = "n/a"

    overall = "ok" if all(v == "ok" or v == "n/a" for v in components.values()) else "degraded"
    return {"status": overall, "components": components}
