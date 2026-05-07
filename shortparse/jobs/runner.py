from shortparse.client import WarcraftLogsClient
from shortparse.report_parser import extract_report_code
from shortparse.selector import select_best_boss_encounters

from shortparse.reports.analysis import build_fight_analysis
from shortparse.reports.export import save_analysis_json

from shortparse.jobs.store import (
    mark_job_completed,
    mark_job_failed,
    mark_job_running,
)

from shortparse.logging import get_logger


logger = get_logger(__name__)


def run_analysis_job(
    job: dict,
) -> dict | None:
    job_id = job["job_id"]
    report_url = job["report_url"]
    report_code = job.get("report_code") or extract_report_code(report_url)

    logger.info(
        "Starting analysis job: job_id=%s report=%s",
        job_id,
        report_code,
    )

    mark_job_running(job_id)

    try:
        client = WarcraftLogsClient()
        report = client.get_report_fights(report_code)

        selected = select_best_boss_encounters(
            report["fights"],
        )

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

                logger.info(
                    "Completed job fight analysis: job_id=%s report=%s fight_id=%s boss=%s",
                    job_id,
                    report_code,
                    fight["id"],
                    analysis["fight"]["name"],
                )

        result = {
            "report": {
                "code": report_code,
                "title": report["title"],
            },
            "analyses": analyses,
        }

        output_path = (
            f"storage/reports/"
            f"{report_code}/"
            f"{job_id}.json"
        )

        save_analysis_json(
            result,
            output_path,
        )

        updated_job = mark_job_completed(
            job_id,
            result_path=output_path,
        )

        logger.info(
            "Completed analysis job: job_id=%s report=%s result=%s",
            job_id,
            report_code,
            output_path,
        )

        return updated_job

    except Exception as error:
        logger.exception(
            "Analysis job failed: job_id=%s report=%s",
            job_id,
            report_code,
        )

        return mark_job_failed(
            job_id,
            str(error),
        )