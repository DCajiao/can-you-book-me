from flask import Blueprint, jsonify, request

from services.gcalendar import GoogleCalendarService
from utils.logger import get_logger

logger = get_logger(__name__)
calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/api/events", methods=["GET"])
def get_events():
    """Devuelve eventos en formato FullCalendar. Público."""
    time_min = request.args.get("start")
    time_max = request.args.get("end")

    if not time_min or not time_max:
        return jsonify({"error": "Se requieren los parámetros start y end"}), 400

    service = GoogleCalendarService()
    events = service.list_events(time_min=time_min, time_max=time_max)
    return jsonify(events)
