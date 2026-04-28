from typing import Any, Callable, Dict, Type, Union

from modules.shared.domain.command import Command
from modules.shared.domain.command_bus import CommandBus
from modules.shared.domain.command_handler import CommandHandler
from .command_handlers import CommandHandlers


class InMemoryCommandBus(CommandBus):
    def __init__(
        self,
        handlers: Union[CommandHandlers, Dict[Type[Command], Callable[[Command], Any]]]
    ) -> None:
        if isinstance(handlers, CommandHandlers):
            self._handlers = handlers
        else:
            self._handlers = CommandHandlers(handlers)

    def dispatch(self, command: Command) -> Any:
        handler = self._handlers.get(command)
        if isinstance(handler, CommandHandler):
            return handler.handle(command)
        return handler(command)
