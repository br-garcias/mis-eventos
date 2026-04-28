from .command import Command


class CommandNotRegisteredError(Exception):
    def __init__(self, command: Command) -> None:
        command_class = command.__class__.__name__
        super().__init__(f"The command <{command_class}> has not a registered handler")
        self._command = command

    @property
    def command(self) -> Command:
        return self._command
