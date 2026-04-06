from flask import Flask

from security.credentials_manager import CredentialsManager
from routes.stats import stats_bp
    

CREDENTIALS = CredentialsManager.get_credentials()


def create_app():
    app = Flask(__name__)

    # register blueprints
    app.register_blueprint(stats_bp, url_prefix="/api")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=int(
        CREDENTIALS.get("PORT", 8080)))