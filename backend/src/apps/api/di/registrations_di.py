from typing import Any, Callable, Dict, Type

from modules.registration_views.application.invalidate_cache.invalidate_registration_views_cache import (
    InvalidateRegistrationViewsCache,
)
from modules.registration_views.domain.registration_view_repository import (
    RegistrationViewRepository,
)
from modules.registrations.application.cancel.cancel_registration_command import (
    CancelRegistrationCommand,
)
from modules.registrations.application.cancel.cancel_registration_command_handler import (
    CancelRegistrationCommandHandler,
)
from modules.registrations.application.cancel.cancel_registration_service import (
    CancelRegistrationService,
)
from modules.registrations.application.cancel_by_event.cancel_registration_by_event_command import (
    CancelRegistrationByEventCommand,
)
from modules.registrations.application.cancel_by_event.cancel_registration_by_event_command_handler import (
    CancelRegistrationByEventCommandHandler,
)
from modules.registrations.application.cancel_by_event.cancel_registration_by_event_service import (
    CancelRegistrationByEventService,
)
from modules.registrations.application.register.register_to_event_command import (
    RegisterToEventCommand,
)
from modules.registrations.application.register.register_to_event_command_handler import (
    RegisterToEventCommandHandler,
)
from modules.registrations.application.register.register_to_event_service import (
    RegisterToEventService,
)
from modules.registrations.domain.registration_repository import RegistrationRepository
from modules.registrations.infrastructure.persistence.mongo_registration_repository import (
    MongoRegistrationRepository,
)
from modules.shared.domain.command import Command

from .cache_di import cache
from .shared_di import mongo_client
from .events_di import event_repository
from .registration_views_di import registration_view_repository

registration_repo: RegistrationRepository = MongoRegistrationRepository(mongo_client)

_registration_views_repo: RegistrationViewRepository = registration_view_repository()
_invalidate_registration_views_cache = InvalidateRegistrationViewsCache(_registration_views_repo)


def registrations_command_handlers() -> Dict[Type[Command], Callable[[Command], Any]]:
    return {
        RegisterToEventCommand: RegisterToEventCommandHandler(
            RegisterToEventService(
                event_repo=event_repository,
                registration_repo=registration_repo,
                cache_invalidator=_invalidate_registration_views_cache,
            )
        ),
        CancelRegistrationCommand: CancelRegistrationCommandHandler(
            CancelRegistrationService(
                event_repo=event_repository,
                registration_repo=registration_repo,
                cache_invalidator=_invalidate_registration_views_cache,
            )
        ),
        CancelRegistrationByEventCommand: CancelRegistrationByEventCommandHandler(
            CancelRegistrationByEventService(
                registration_repo=registration_repo,
                cancel_service=CancelRegistrationService(
                    event_repo=event_repository,
                    registration_repo=registration_repo,
                    cache_invalidator=_invalidate_registration_views_cache,
                ),
            ),
        ),
    }
