from flask import Blueprint, redirect, request, jsonify

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
    auth_url = service.get_auth_url()
    return redirect(auth_url)


@admin_bp.route("/admin/callback", methods=["GET"])
def callback():
    """Recibe el código de Google y lo intercambia por tokens."""
    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return jsonify({"error": "Parámetros incompletos en el callback"}), 400

    service = GoogleCalendarService()
    tokens = service.exchange_code(code, state=state)

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
