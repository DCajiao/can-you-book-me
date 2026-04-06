import logging

from security.credentials_manager import CredentialsManager
CREDENTIALS = CredentialsManager.get_credentials()

logging.basicConfig(level=CREDENTIALS.get("LOGGER_LEVEL", "INFO"))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name (str): The name of the module or class.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
