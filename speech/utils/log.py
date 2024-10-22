import logging
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)


class ColoredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Create a console handler and set the level
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)

        # Create a formatter and set it to the handler
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(handler)

    def _format_message(self, *args):
        """Helper function to format multiple arguments into a single message string"""
        return " ".join(str(arg) for arg in args)

    def info(self, *args):
        message = self._format_message(*args)
        self.logger.info(Fore.GREEN + message + Style.RESET_ALL)

    def warn(self, *args):
        message = self._format_message(*args)
        self.logger.warning(Fore.YELLOW + message + Style.RESET_ALL)

    def error(self, *args):
        message = self._format_message(*args)
        self.logger.error(Fore.RED + message + Style.RESET_ALL)


log = ColoredLogger(__name__)

# log.info("This is an", "info message with", "multiple arguments")
# log.warn("This is", "a warning", "with more info")
# log.error("An error occurred:", "Error code", 404)
