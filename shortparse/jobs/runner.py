from shortparse.settings import REPORTS_DIR

from shortparse.client import WarcraftLogsClient
from shortparse.report_parser import extract_report_code
from shortparse.selector import select_best_boss_encounters, group_all_boss_encounters

from shortparse.reports.analysis import build_fight_analysis, aggregate_pull_analyses
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

        # If this job belongs to a registered user, use their personal Warcraft Logs OAuth token
        user_access_token = None
        use_user_endpoint = False

        user_id = job.get("user_id")
        if user_id:
            from shortparse.database import SessionLocal
            from shortparse.server.auth_helpers import get_valid_wcl_account

            db = SessionLocal()
            try:
                account = get_valid_wcl_account(db, user_id)
                if account:
                    user_access_token = account.access_token
                    use_user_endpoint = True
                    append_job_log(
                        job_id,
                        "Using linked Warcraft Logs account for private report access.",
                        progress=12,
                        current_step="Using Warcraft Logs OAuth",
                    )
            except Exception as e:
                logger.error("Failed to load user Warcraft Logs OAuth token: %s", e)
                append_job_log(
                    job_id,
                    "Could not use your linked Warcraft Logs account. Private reports may fail.",
                    level="warning",
                    progress=12,
                    current_step="Warcraft Logs OAuth unavailable",
                )
            finally:
                db.close()

        client = WarcraftLogsClient(
            access_token=user_access_token,
            use_user_endpoint=use_user_endpoint,
        )

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
            "Selecting all boss encounter pulls...",
            progress=26,
            current_step="Selecting encounters",
        )

        grouped_encounters = group_all_boss_encounters(
            report["fights"],
        )

        all_fights_flat = []
        for raid_name, bosses in grouped_encounters.items():
            for boss_key, boss_fights in bosses.items():
                all_fights_flat.extend(boss_fights)

        total_fights = len(all_fights_flat)

        append_job_log(
            job_id,
            f"Selected {total_fights} boss pull(s) across {sum(len(bosses) for bosses in grouped_encounters.values())} encounter(s) for analysis.",
            progress=30,
            current_step="Encounters selected",
        )

        # Pre-fetch player data and events concurrently for all encounters to merge API wait times
        append_job_log(
            job_id,
            "Pre-downloading player details and fight events concurrently...",
            progress=32,
            current_step="Pre-fetching data",
        )

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
            # Limit concurrent WCL API calls to 3 to prevent rate limit (HTTP 429) errors
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(all_fights_flat), 3)) as executor:
                futures = [executor.submit(fetch_fight_resources, f) for f in all_fights_flat]
                for future in concurrent.futures.as_completed(futures):
                    fid, f_data, evts = future.result()
                    fight_resources[fid] = (f_data, evts)

        analyses = []

        base_progress = 30
        fight_progress_range = 55
        fights_processed_count = 0

        for raid_name, bosses in grouped_encounters.items():
            append_job_log(
                job_id,
                f"Raid detected: {raid_name}",
                current_step=f"Processing {raid_name}",
            )

            for boss_key, boss_fights in bosses.items():
                boss_name = boss_fights[0].get("name", "Unknown Boss")
                
                # Analyze each pull for this boss encounter
                pull_analyses = []
                for idx, fight in enumerate(boss_fights, start=1):
                    fights_processed_count += 1
                    
                    current_progress = int(
                        base_progress
                        + (
                            (fights_processed_count - 1)
                            / max(total_fights, 1)
                        )
                        * fight_progress_range
                    )

                    result_type = "kill" if fight.get("kill") else "wipe"
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
                            f"(Pull {idx}/{len(boss_fights)}) "
                            f"- {result_type}, {boss_hp_text}."
                        ),
                        progress=current_progress,
                        current_step=f"Analyzing {boss_name}",
                    )

                    # Pop the resources so that Python's garbage collector can reclaim memory immediately after this fight is processed
                    fight_data, events = fight_resources.pop(fight["id"])

                    append_job_log(
                        job_id,
                        f"{boss_name} (Pull {idx}): building scorecard, mechanics and timeline...",
                        current_step=f"{boss_name} (Pull {idx}): building",
                    )

                    pull_analysis = build_fight_analysis(
                        report_code,
                        report["title"],
                        fight,
                        fight_data,
                        events,
                        progress_callback=lambda message, boss_name=boss_name, idx=idx: append_job_log(
                            job_id,
                            f"{boss_name} (Pull {idx}): {message}",
                            current_step=f"{boss_name}: {message}",
                        ),
                    )

                    pull_analysis["raid"] = {
                        "name": raid_name,
                    }
                    
                    pull_analyses.append(pull_analysis)

                # Now aggregate all pull analyses for this boss encounter!
                append_job_log(
                    job_id,
                    f"{boss_name}: aggregating {len(pull_analyses)} pull(s)...",
                    current_step=f"{boss_name}: aggregating pulls",
                )
                
                # Build the boss progression list for metadata
                boss_pulls = []
                for idx, a in enumerate(pull_analyses, start=1):
                    f_meta = a["fight"]
                    boss_pulls.append({
                        "pull_number": idx,
                        "fight_id": f_meta.get("id"),
                        "kill": f_meta.get("kill", False),
                        "boss_percentage": f_meta.get("boss_percentage"),
                        "fight_percentage": f_meta.get("fight_percentage"),
                        "duration_seconds": f_meta.get("duration_seconds"),
                        "last_phase": f_meta.get("phase") or 1,
                        "last_phase_index": f_meta.get("phase") or 0,
                        "start_time": f_meta.get("start_time"),
                        "end_time": f_meta.get("end_time")
                    })
                
                aggregated_analysis = aggregate_pull_analyses(
                    pull_analyses,
                    report_code,
                    report["title"],
                )
                
                aggregated_analysis["raid"] = {
                    "name": raid_name,
                }
                
                aggregated_analysis["progression"] = {
                    "pulls": boss_pulls
                }
                
                analyses.append(aggregated_analysis)

                completed_progress = int(
                    base_progress
                    + (
                        fights_processed_count
                        / max(total_fights, 1)
                    )
                    * fight_progress_range
                )

                append_job_log(
                    job_id,
                    f"{boss_name}: complete. Successfully aggregated {len(pull_analyses)} pull(s).",
                    level="success",
                    progress=completed_progress,
                    current_step=f"{boss_name}: complete",
                )

                logger.info(
                    "Completed job encounter analysis: job_id=%s report=%s boss=%s pulls=%s",
                    job_id,
                    report_code,
                    boss_name,
                    len(pull_analyses),
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