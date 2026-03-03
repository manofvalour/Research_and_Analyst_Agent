from .custom_logger import CustomLogger

## creating a single share logger instance
GLOBAL_LOGGER = CustomLogger().get_logger("research_and_analyst")
