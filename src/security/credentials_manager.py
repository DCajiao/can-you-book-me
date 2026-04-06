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
            # Google OAuth2 (Calendar)
            "SECRET_KEY": os.getenv("SECRET_KEY"),
            "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
            "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
            "GOOGLE_REFRESH_TOKEN": os.getenv("GOOGLE_REFRESH_TOKEN"),
            "GOOGLE_REDIRECT_URI": os.getenv("GOOGLE_REDIRECT_URI", "http://127.0.0.1:5000/admin/callback"),
            "CALENDAR_IDS": os.getenv("CALENDAR_IDS", "primary"),
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