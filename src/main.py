import os
from flask import Flask, render_template

from security.credentials_manager import CredentialsManager
from routes.stats import stats_bp
from routes.admin import admin_bp
from routes.calendar import calendar_bp


CREDENTIALS = CredentialsManager.get_credentials()


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )

    app.secret_key = CREDENTIALS.get("SECRET_KEY", "dev-secret-change-me")

    # blueprints
    app.register_blueprint(stats_bp, url_prefix="/api")
    app.register_blueprint(admin_bp)
    app.register_blueprint(calendar_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=int(CREDENTIALS.get("PORT", 8080)))
