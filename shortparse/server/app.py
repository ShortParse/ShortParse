from fastapi import FastAPI
from pydantic import BaseModel

from shortparse.client import WarcraftLogsClient
from shortparse.report_parser import extract_report_code
from shortparse.selector import select_best_boss_encounters
from shortparse.reports.analysis import build_fight_analysis


app = FastAPI(
    title="ShortParse API",
    version="0.1.0",
)


class AnalyzeRequest(BaseModel):
    report_url: str


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
    }


@app.post("/analyze")
def analyze_report(request: AnalyzeRequest) -> dict:
    report_code = extract_report_code(request.report_url)

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

            analysis["raid"] = {
                "name": raid_name,
            }

            analyses.append(analysis)

    return {
        "report": {
            "code": report_code,
            "title": report["title"],
        },
        "analyses": analyses,
    }