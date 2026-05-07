from fastapi import FastAPI
from pydantic import BaseModel

from shortparse.client import WarcraftLogsClient
from shortparse.report_parser import extract_report_code
from shortparse.selector import select_best_boss_encounters
from shortparse.reports.analysis import build_fight_analysis
from shortparse.reports.serializers import serialize_analysis
from shortparse.logging import get_logger


logger = get_logger(__name__)

app = FastAPI(
    title="ShortParse API",
    version="0.1.0",
)


class AnalyzeRequest(BaseModel):
    report_url: str


@app.get("/health")
def health_check() -> dict:
    logger.info("Health check requested")

    return {
        "status": "ok",
    }


@app.post("/analyze")
def analyze_report(request: AnalyzeRequest) -> dict:
    report_code = extract_report_code(request.report_url)

    logger.info(
        "API analysis requested for report %s",
        report_code,
    )

    client = WarcraftLogsClient()
    report = client.get_report_fights(report_code)

    selected = select_best_boss_encounters(report["fights"])

    analyses = []

    for raid_name, fights in selected.items():
        for fight in fights:
            fight_data = client.get_fight_player_data(
                report_code,
                fight["id"],
            )

            events = client.get_fight_events(
                report_code,
                fight["id"],
                fight["startTime"],
                fight["endTime"],
            )

            analysis = build_fight_analysis(
                report_code,
                report["title"],
                fight,
                fight_data,
                events,
            )

            logger.info(
                "Completed fight analysis: report=%s fight_id=%s boss=%s",
                report_code,
                fight["id"],
                analysis["fight"]["name"],
            )

            analysis["raid"] = {
                "name": raid_name,
            }

            analyses.append(
                serialize_analysis(analysis)
            )

    logger.info(
        "Completed report analysis: report=%s fights=%s",
        report_code,
        len(analyses),
    )

    return {
        "report": {
            "code": report_code,
            "title": report["title"],
        },
        "analyses": analyses,
    }