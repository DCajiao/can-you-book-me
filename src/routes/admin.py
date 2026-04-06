from flask import Blueprint, redirect, request, jsonify, session

from security.auth import require_api_key
from services.gcalendar import GoogleCalendarService
from utils.logger import get_logger

logger = get_logger(__name__)
admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/setup", methods=["GET"])
@require_api_key
def setup():
    """Inicia el flujo OAuth2. Usar una sola vez para obtener el refresh token."""
    service = GoogleCalendarService()
    auth_url, code_verifier = service.get_auth_url()
    session["oauth_code_verifier"] = code_verifier
    return redirect(auth_url)


@admin_bp.route("/admin/callback", methods=["GET"])
def callback():
    """Recibe el código de Google y lo intercambia por tokens."""
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "No authorization code received"}), 400

    code_verifier = session.pop("oauth_code_verifier", None)
    service = GoogleCalendarService()
    tokens = service.exchange_code(code, code_verifier=code_verifier)

    refresh_token = tokens.get("refresh_token")
    if refresh_token:
        logger.info("=" * 60)
        logger.info("GOOGLE_REFRESH_TOKEN=%s", refresh_token)
        logger.info("Copia este valor a tu .env como GOOGLE_REFRESH_TOKEN")
        logger.info("=" * 60)

    return jsonify({
        "message": "Autenticación exitosa. Copia el GOOGLE_REFRESH_TOKEN de los logs al .env.",
        "refresh_token": refresh_token,
    })
