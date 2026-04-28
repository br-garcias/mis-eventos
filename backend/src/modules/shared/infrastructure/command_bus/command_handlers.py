from typing import Any, Callable, Dict, List, Union, Type

from modules.shared.domain.command import Command
from modules.shared.domain.command_handler import CommandHandler
from modules.shared.domain.command_not_registered_error import CommandNotRegisteredError


class CommandHandlers:
    def __init__(
        self,
        handlers: Union[List[CommandHandler], Dict[Type[Command], Callable[[Command], Any]]]
    ) -> None:
        if isinstance(handlers, dict):
            self._handlers = dict(handlers)
        else:
            self._handlers = {}
            for handler in handlers:
                self._handlers[handler.subscribed_to()] = handler

    def get(self, command: Command) -> Union[Callable[[Command], Any], CommandHandler]:
        handler = self._handlers.get(type(command))
        if handler is None:
            raise CommandNotRegisteredError(command)
        return handler

    def register(
        self,
        command_class: Type[Command],
        handler: Union[Callable[[Command], Any], CommandHandler]
    ) -> None:
        self._handlers[command_class] = handler
