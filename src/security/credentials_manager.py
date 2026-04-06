import os
from dotenv import load_dotenv


class CredentialsManager:
    @staticmethod
    def get_credentials():
        """
        Loads environment variables from a .env file and returns
        a dictionary.
        """
        load_dotenv()

        credentials = {
            "API_KEY": os.getenv("API_KEY"),
            "PORT": os.getenv("PORT"),
            "LOGGER_LEVEL": os.getenv("LOGGER_LEVEL", "INFO"),
            # SSH Tunnel
            "SSH_HOST": os.getenv("SSH_HOST"),
            "SSH_PORT": os.getenv("SSH_PORT", "22"),
            "SSH_USER": os.getenv("SSH_USER"),
            "SSH_PASS": os.getenv("SSH_PASS"),
            # MySQL
            "MYSQL_USER": os.getenv("MYSQL_USER"),
            "MYSQL_PASS": os.getenv("MYSQL_PASS"),
            "MYSQL_DB": os.getenv("MYSQL_DB"),
            "WP_TABLE_PREFIX": os.getenv("WP_TABLE_PREFIX", "wp_"),
            # GCP
            "GCP_PROJECT": os.getenv("GCP_PROJECT"),
            "GCP_SERVICE_ACCOUNT_JSON": os.getenv("GCP_SERVICE_ACCOUNT_JSON"),
        }

        # Only validate core app variables (sync vars validated at runtime)
        required = ["API_KEY", "PORT"]
        missing = [key for key in required if not credentials.get(key)]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please check your .env file."
            )

        return credentials