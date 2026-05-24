from shortparse.settings import REPORTS_DIR

from shortparse.client import WarcraftLogsClient
from shortparse.report_parser import extract_report_code
from shortparse.selector import select_best_boss_encounters

from shortparse.reports.analysis import build_fight_analysis
from shortparse.reports.export import save_analysis_json

from shortparse.jobs.store import (
    append_job_log,
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

    append_job_log(
        job_id,
        "Analysis job started.",
        progress=5,
        current_step="Starting analysis",
    )

    try:
        append_job_log(
            job_id,
            "Connecting to Warcraft Logs...",
            progress=10,
            current_step="Connecting",
        )

        client = WarcraftLogsClient()

        append_job_log(
            job_id,
            f"Fetching report metadata for {report_code}...",
            progress=15,
            current_step="Fetching report",
        )

        report = client.get_report_fights(report_code)

        append_job_log(
            job_id,
            f"Report loaded: {report.get('title', 'Unknown Report')}",
            progress=22,
            current_step="Report loaded",
        )

        append_job_log(
            job_id,
            "Selecting boss kills and best progression wipes...",
            progress=26,
            current_step="Selecting encounters",
        )

        selected = select_best_boss_encounters(
            report["fights"],
        )

        total_fights = sum(
            len(fights)
            for fights in selected.values()
        )

        append_job_log(
            job_id,
            f"Selected {total_fights} boss encounter(s) for analysis.",
            progress=30,
            current_step="Encounters selected",
        )

        # Pre-fetch player data and events concurrently for all selected encounters to merge API wait times
        append_job_log(
            job_id,
            "Pre-downloading player details and fight events concurrently...",
            progress=32,
            current_step="Pre-fetching data",
        )

        all_fights_flat = []
        for fights in selected.values():
            all_fights_flat.extend(fights)

        import concurrent.futures

        def fetch_fight_resources(f):
            append_job_log(
                job_id,
                f"Pre-fetching {f.get('name', 'Unknown')}: downloading data and events...",
                current_step="Pre-fetching",
            )
            f_data = client.get_fight_player_data(report_code, f["id"])
            evts = client.get_fight_events(
                report_code,
                f["id"],
                f["startTime"],
                f["endTime"],
            )
            return f["id"], f_data, evts

        fight_resources = {}
        if all_fights_flat:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(all_fights_flat), 10)) as executor:
                futures = [executor.submit(fetch_fight_resources, f) for f in all_fights_flat]
                for future in concurrent.futures.as_completed(futures):
                    fid, f_data, evts = future.result()
                    fight_resources[fid] = (f_data, evts)

        analyses = []

        base_progress = 30
        fight_progress_range = 55

        for raid_name, fights in selected.items():
            append_job_log(
                job_id,
                f"Raid detected: {raid_name}",
                current_step=f"Processing {raid_name}",
            )

            for fight in fights:
                fight_number = len(analyses) + 1
                boss_name = fight.get("name", "Unknown Boss")

                current_progress = int(
                    base_progress
                    + (
                        (fight_number - 1)
                        / max(total_fights, 1)
                    )
                    * fight_progress_range
                )

                result_type = "kill" if fight.get("kill") else "best wipe"

                boss_percentage = fight.get("bossPercentage")
                boss_hp_text = (
                    f"{boss_percentage}% boss HP remaining"
                    if boss_percentage is not None
                    else "boss HP unknown"
                )

                append_job_log(
                    job_id,
                    (
                        f"Analyzing {boss_name} "
                        f"({fight_number}/{total_fights}) "
                        f"- selected {result_type}, {boss_hp_text}."
                    ),
                    progress=current_progress,
                    current_step=f"Analyzing {boss_name}",
                )

                append_job_log(
                    job_id,
                    f"{boss_name}: retrieving pre-fetched data...",
                    current_step=f"{boss_name}: reading data",
                )

                fight_data, events = fight_resources[fight["id"]]

                append_job_log(
                    job_id,
                    (
                        f"{boss_name}: building mechanics, scorecards, "
                        "cooldowns, benchmarks, and timeline..."
                    ),
                    current_step=f"{boss_name}: building analysis",
                )

                analysis = build_fight_analysis(
                    report_code,
                    report["title"],
                    fight,
                    fight_data,
                    events,
                    progress_callback=lambda message, boss_name=boss_name: append_job_log(
                        job_id,
                        f"{boss_name}: {message}",
                        current_step=f"{boss_name}: {message}",
                    ),
                )

                analysis["raid"] = {
                    "name": raid_name,
                }

                analyses.append(analysis)

                completed_progress = int(
                    base_progress
                    + (
                        fight_number
                        / max(total_fights, 1)
                    )
                    * fight_progress_range
                )

                mechanic_count = len(
                    analysis.get("mechanics", {})
                    .get("raid_mechanics", {})
                )

                player_count = len(
                    analysis.get("roster", [])
                )

                issue_count = len(
                    analysis.get("issues", [])
                )

                append_job_log(
                    job_id,
                    (
                        f"{boss_name}: complete. "
                        f"{player_count} players, "
                        f"{mechanic_count} tracked mechanics, "
                        f"{issue_count} issues found."
                    ),
                    level="success",
                    progress=completed_progress,
                    current_step=f"{boss_name}: complete",
                )

                logger.info(
                    "Completed job fight analysis: job_id=%s report=%s fight_id=%s boss=%s",
                    job_id,
                    report_code,
                    fight["id"],
                    analysis["fight"]["name"],
                )

        append_job_log(
            job_id,
            "Finalizing report...",
            progress=90,
            current_step="Finalizing report",
        )

        result = {
            "report": {
                "code": report_code,
                "title": report["title"],
            },
            "analyses": analyses,
        }

        output_path = str(
            REPORTS_DIR
            / report_code
            / f"{job_id}.json"
        )

        append_job_log(
            job_id,
            "Saving report result...",
            progress=95,
            current_step="Saving report",
        )

        save_analysis_json(
            result,
            output_path,
        )

        append_job_log(
            job_id,
            "Report saved successfully.",
            level="success",
            progress=98,
            current_step="Report saved",
        )

        updated_job = mark_job_completed(
            job_id,
            result_path=output_path,
        )

        append_job_log(
            job_id,
            "Analysis complete. Report is ready.",
            level="success",
            progress=100,
            current_step="Complete",
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

        append_job_log(
            job_id,
            f"Analysis failed: {error}",
            level="error",
            progress=100,
            current_step="Failed",
        )

        return mark_job_failed(
            job_id,
            str(error),
        )