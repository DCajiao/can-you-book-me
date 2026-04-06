from flask import Blueprint, jsonify

import psutil

from security.credentials_manager import CredentialsManager
from utils.logger import get_logger

CREDENTIALS = CredentialsManager.get_credentials()
logger = get_logger(__name__)
stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/system/usage", methods=["GET"])
def system_usage():
    cpu_percent = psutil.cpu_percent(interval=0.5)

    memory = psutil.virtual_memory()
    ram_usage = {
        "total_mb": round(memory.total / (1024 ** 2), 2),
        "used_mb": round(memory.used / (1024 ** 2), 2),
        "available_mb": round(memory.available / (1024 ** 2), 2),
        "percent": memory.percent
    }

    logger.debug(f"CPU Usage: {cpu_percent}%, RAM Usage: {ram_usage}")

    return jsonify({
        "cpu_percent": cpu_percent,
        "ram": ram_usage
    }), 200
