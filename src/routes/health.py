from flask import Blueprint, jsonify
from security.credentials_manager import CredentialsManager


CREDENTIALS = CredentialsManager.get_credentials()
health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "flask-api",
        "port": CREDENTIALS.get("PORT", 5000)
    }), 200
