import httpx

from src.common.config import get_settings
from src.common.logging import get_logger

logger = get_logger(__name__)


def send_alert(alert_type: str, message: str) -> bool:
    settings = get_settings()
    if not settings.alert_webhook_url:
        logger.warning("Alert webhook is not configured", extra={"alert_type": alert_type})
        return False
    payload = {
        "alert_type": alert_type,
        "message": message,
        "environment": settings.app_env,
        "source": "ecommerce-price-monitor",
    }
    try:
        response = httpx.post(settings.alert_webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except httpx.HTTPError as error:
        logger.error("Alert delivery failed: %s", error)
        return False
