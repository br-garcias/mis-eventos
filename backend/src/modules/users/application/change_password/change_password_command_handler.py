from modules.shared.domain.command_handler import CommandHandler
from .change_password_command import ChangePasswordCommand
from .password_changer import PasswordChanger


class ChangePasswordCommandHandler(CommandHandler):
    def __init__(self, changer: PasswordChanger) -> None:
        self._changer = changer

    def subscribed_to(self):
        return ChangePasswordCommand

    def handle(self, command: ChangePasswordCommand) -> None:
        self._changer.run(
            user_id=command.user_id,
            current_password=command.current_password,
            new_password=command.new_password,
        )
