from google.cloud import bigquery

from utils.logger import get_logger
from security.gcp_auth import get_gcp_credentials

logger = get_logger(__name__)


class BigQueryClient:
    """BigQuery client with centralized GCP authentication (service account or ADC)."""

    def __init__(self, service_account_json: str | None = None):
        credentials = get_gcp_credentials(service_account_json)
        self.client = bigquery.Client(credentials=credentials)
        logger.info("BigQuery client initialized (project=%s)",
                    self.client.project)
