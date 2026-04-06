import os
from google.oauth2 import service_account
from google.auth.credentials import Credentials

from utils.logger import get_logger

logger = get_logger(__name__)


def get_gcp_credentials(service_account_json: str | None = None) -> Credentials | None:
    """
    Gets GCP credentials using service account or ADC.

    Args:
        service_account_json: Path to service account JSON file (optional)

    Returns:
        Credentials if using service account, None if using ADC
    """
    if service_account_json and os.path.exists(service_account_json):
        logger.info("GCP auth: using service account file '%s'", service_account_json)
        return service_account.Credentials.from_service_account_file(
            service_account_json
        )

    if service_account_json:
        logger.warning(
            "GCP auth: service account path '%s' not found, falling back to ADC",
            service_account_json,
        )
    else:
        logger.info("GCP auth: no service account configured, using ADC")

    return None