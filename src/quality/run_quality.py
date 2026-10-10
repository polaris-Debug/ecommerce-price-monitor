import json
import re
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import text

from src.alerts.notifier import send_alert
from src.common.config import get_settings
from src.common.db import create_db_engine, create_session_factory, session_scope
from src.common.logging import configure_logging, get_logger
from src.quality.expectations import EXPECTATIONS

logger = get_logger(__name__)


def evaluate(value: float, expectation: str) -> bool:
    expression = re.sub(r"(?<![=!<>])=(?!=)", "==", expectation)
    return bool(eval(expression, {"__builtins__": {}}, {"value": value}))  # noqa: S307


def run_quality_report() -> dict:
    settings = get_settings()
    configure_logging(settings.log_level)
    engine = create_db_engine(settings.mysql_url)
    session_factory = create_session_factory(engine)
    checks = []
    try:
        with session_scope(session_factory) as session:
            for expectation in EXPECTATIONS:
                value = float(session.execute(text(expectation.query)).scalar() or 0)
                checks.append(
                    {
                        "name": expectation.name,
                        "value": value,
                        "expectation": expectation.expectation,
                        "severity": expectation.severity,
                        "passed": evaluate(value, expectation.expectation),
                    }
                )
        passed_count = sum(bool(check["passed"]) for check in checks)
        score = round(passed_count / len(checks), 4) if checks else 0.0
        report = {
            "generated_at": datetime.now(UTC).isoformat(),
            "score": score,
            "passed": passed_count,
            "failed": len(checks) - passed_count,
            "checks": checks,
        }
        output = Path(settings.report_dir)
        output.mkdir(parents=True, exist_ok=True)
        (output / "data_quality_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if score < settings.data_quality_score_threshold:
            message = (
                f"Data quality score {score:.2%} is below threshold "
                f"{settings.data_quality_score_threshold:.2%}"
            )
            logger.error(message)
            send_alert("DATA_QUALITY_ALERT", message)
        else:
            logger.info("Data quality passed", extra={"score": score})
        return report
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_quality_report()
