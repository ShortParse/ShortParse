from rich.console import Console
from rich.table import Table

from shortparse.client import WarcraftLogsClient
from shortparse.players import build_roster_from_fight_data
from shortparse.report_parser import extract_report_code
from shortparse.selector import select_best_boss_encounters

from shortparse.metrics.builder import build_player_metrics
from shortparse.metrics.issues import build_raid_issues
from shortparse.metrics.mechanics import calculate_mechanics
from shortparse.metrics.timeline import build_timeline

from shortparse.benchmarks.builder import build_benchmark_comparisons
from shortparse.benchmarks.grading import calculate_grade

from shortparse.reports.scorecard import build_scorecard


console = Console(width=180)


def format_number(value: int) -> str:
    return f"{value:,}"


def format_duration(start_time: float, end_time: float) -> str:
    duration_seconds = int((end_time - start_time) / 1000)
    minutes = duration_seconds // 60
    seconds = duration_seconds % 60
    return f"{minutes}:{seconds:02d}"


def print_encounter_summary(raid_name: str, fights: list[dict]) -> None:
    console.print(f"[bold yellow]{raid_name}[/bold yellow]")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Boss")
    table.add_column("Fight ID")
    table.add_column("Result")
    table.add_column("Boss HP Left")
    table.add_column("Progress")
    table.add_column("Phase")
    table.add_column("Duration")

    for fight in fights:
        result = "KILL" if fight.get("kill") else "BEST WIPE"

        boss_hp = fight.get("bossPercentage")
        boss_hp_text = "Unknown" if boss_hp is None else f"{boss_hp:.2f}%"

        fight_percentage = fight.get("fightPercentage")
        progress_text = "Unknown" if fight_percentage is None else f"{fight_percentage:.2f}%"

        phase = fight.get("lastPhaseAsAbsoluteIndex")
        phase_text = "Unknown" if phase is None else str(phase)

        table.add_row(
            fight.get("name", "Unknown"),
            str(fight.get("id")),
            result,
            boss_hp_text,
            progress_text,
            phase_text,
            format_duration(fight["startTime"], fight["endTime"]),
        )

    console.print(table)
    console.print()


def print_roster_table(boss_name: str, roster: list[dict]) -> None:
    console.print(f"[bold cyan]Roster: {boss_name}[/bold cyan]")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Player")
    table.add_column("Class")
    table.add_column("Spec")
    table.add_column("Role")
    table.add_column("iLvl")
    table.add_column("Damage")
    table.add_column("Healing")
    table.add_column("Dmg Taken")

    for player in roster:
        table.add_row(
            player["name"],
            str(player["class"]),
            str(player["spec"]),
            str(player["role"]),
            str(player["item_level"]),
            format_number(player["damage_done"]),
            format_number(player["healing_done"]),
            format_number(player["damage_taken"]),
        )

    console.print(table)
    console.print()


def print_metrics_table(boss_name: str, player_metrics: dict) -> None:
    console.print(f"[bold magenta]Metrics: {boss_name}[/bold magenta]")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Player")
    table.add_column("Role")
    table.add_column("Active %")
    table.add_column("Inactive")
    table.add_column("Deaths")
    table.add_column("Avoid Hits")
    table.add_column("Avoid Dmg")
    table.add_column("DPS")
    table.add_column("HPS")
    table.add_column("Pots")
    table.add_column("HS")

    for player_name, metric_data in sorted(player_metrics.items()):
        identity = metric_data["identity"]
        activity = metric_data["activity"]
        performance = metric_data["performance"]
        consumables = metric_data["consumables"]

        table.add_row(
            player_name,
            identity["role"],
            f'{activity["active_time_pct"]:.2f}%',
            f'{activity["inactive_seconds"]:.2f}s',
            str(performance.get("deaths", 0)),
            str(performance.get("avoidable_hit_count", 0)),
            format_number(
                performance.get("avoidable_damage_taken", 0)
            ),
            format_number(int(performance.get("dps", 0))),
            format_number(int(performance.get("hps", 0))),
            str(consumables.get("combat_potions", 0)),
            str(consumables.get("healthstone_count", 0)),
        )

    console.print(table)
    console.print()

def print_mechanics_table(
    boss_name: str,
    mechanics_data: dict,
) -> None:
    raid_mechanics = mechanics_data.get("raid_mechanics", {})

    if not raid_mechanics:
        console.print(f"[bold yellow]Mechanics: {boss_name}[/bold yellow]")
        console.print("No tracked mechanics found.\n")
        return

    console.print(f"[bold yellow]Mechanics: {boss_name}[/bold yellow]")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Mechanic")
    table.add_column("Hits")
    table.add_column("Damage")
    table.add_column("Players Hit")
    table.add_column("Worst Player")
    table.add_column("Worst Hits")

    for mechanic_name, mechanic_data in sorted(raid_mechanics.items()):
        players_hit = mechanic_data.get("players_hit", [])

        table.add_row(
            mechanic_name,
            str(mechanic_data.get("hits", 0)),
            format_number(mechanic_data.get("damage", 0)),
            str(len(players_hit)),
            str(mechanic_data.get("worst_player") or ""),
            str(mechanic_data.get("worst_hits", 0)),
        )

    console.print(table)
    console.print()

def print_cooldowns_table(
    boss_name: str,
    player_metrics: dict,
) -> None:
    rows = []

    for player_name, metric_data in sorted(player_metrics.items()):
        cooldowns = metric_data.get("cooldowns", {})

        for cooldown_name, cooldown_data in sorted(cooldowns.items()):
            rows.append(
                {
                    "player": player_name,
                    "cooldown": cooldown_name,
                    "category": cooldown_data.get("category", "Unknown"),
                    "casts": cooldown_data.get("casts", 0),
                    "possible_casts": cooldown_data.get("possible_casts", 0),
                    "efficiency_pct": cooldown_data.get("efficiency_pct", 0.0),
                }
            )

    if not rows:
        console.print(f"[bold cyan]Cooldowns: {boss_name}[/bold cyan]")
        console.print("No tracked cooldowns used.\n")
        return

    console.print(f"[bold cyan]Cooldowns: {boss_name}[/bold cyan]")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Player")
    table.add_column("Cooldown")
    table.add_column("Category")
    table.add_column("Casts")
    table.add_column("Possible")
    table.add_column("Efficiency")

    for row in rows:
        table.add_row(
            row["player"],
            row["cooldown"],
            row["category"],
            str(row["casts"]),
            str(row["possible_casts"]),
            f'{row["efficiency_pct"]:.0f}%',
        )

    console.print(table)
    console.print()

def print_timeline_table(
    boss_name: str,
    timeline: list[dict],
    limit: int = 40,
) -> None:
    console.print(f"[bold white]Timeline: {boss_name}[/bold white]")

    if not timeline:
        console.print("No tracked timeline events found.\n")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Time")
    table.add_column("Type")
    table.add_column("Summary")

    for entry in timeline[:limit]:
        table.add_row(
            entry.get("time", ""),
            entry.get("type", ""),
            entry.get("summary", ""),
        )

    console.print(table)

    if len(timeline) > limit:
        console.print(f"...showing first {limit} of {len(timeline)} timeline events.\n")
    else:
        console.print()

def print_benchmark_table(boss_name: str, comparisons: dict) -> None:
    console.print(f"[bold blue]Benchmarks: {boss_name}[/bold blue]")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Player")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_column("% Top 1")
    table.add_column("% Top 5")
    table.add_column("% Top 10")
    table.add_column("% Bench")
    table.add_column("Grade")

    for player_name, comparison in sorted(comparisons.items()):
        grade = calculate_grade(
            comparison.percent_of_average
        )

        table.add_row(
            player_name,
            comparison.metric.upper(),
            format_number(int(comparison.player_value)),
            "N/A" if comparison.percent_of_top_1 is None else f"{comparison.percent_of_top_1:.2f}%",
            "N/A" if comparison.percent_of_top_5 is None else f"{comparison.percent_of_top_5:.2f}%",
            "N/A" if comparison.percent_of_top_10 is None else f"{comparison.percent_of_top_10:.2f}%",
            "N/A" if comparison.percent_of_average is None else f"{comparison.percent_of_average:.2f}%",
            comparison.grade,
        )

    console.print(table)
    console.print()

def print_issues_table(
    boss_name: str,
    issues: list[dict],
) -> None:

    if not issues:
        console.print(f"[bold green]Issues: {boss_name}[/bold green]")
        console.print("No issues found.\n")
        return

    console.print(f"[bold red]Issues: {boss_name}[/bold red]")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Severity")
    table.add_column("Score")
    table.add_column("Player")
    table.add_column("Category")
    table.add_column("Issue")

    for issue in issues:
        table.add_row(
            issue["severity"],
            str(issue["score"]),
            issue["player"],
            issue["category"],
            issue["message"],
        )

    console.print(table)
    console.print()

def print_scorecard_table(
    boss_name: str,
    player_metrics: dict,
    issues: list[dict],
    benchmark_comparisons: dict,
) -> None:

    scorecard = build_scorecard(
        player_metrics,
        issues,
        benchmark_comparisons,
    )

    console.print(f"[bold green]Scorecard: {boss_name}[/bold green]")

    table = Table(show_header=True, header_style="bold")

    table.add_column("Player")
    table.add_column("Grade")
    table.add_column("Issue Score")
    table.add_column("Critical")
    table.add_column("Major")
    table.add_column("Warning")
    table.add_column("Top Issue")

    for row in scorecard:
        table.add_row(
            row["player"],
            row["grade"],
            str(row["issue_score"]),
            str(row["critical_count"]),
            str(row["major_count"]),
            str(row["warning_count"]),
            row["top_issue"],
        )

    console.print(table)
    console.print()

def main():
    url = input("Paste Warcraft Logs report URL: ").strip()
    report_code = extract_report_code(url)

    client = WarcraftLogsClient()
    report = client.get_report_fights(report_code)

    selected = select_best_boss_encounters(report["fights"])

    console.print(f"\n[bold cyan]ShortParse Report:[/bold cyan] {report['title']}\n")

    for raid_name, fights in selected.items():
        print_encounter_summary(raid_name, fights)

        for fight in fights:
            fight_data = client.get_fight_player_data(report_code, fight["id"])
            roster = build_roster_from_fight_data(fight_data)

            fight_duration_seconds = (
                fight["endTime"] - fight["startTime"]
            ) / 1000

            events = client.get_fight_events(
                report_code,
                fight["id"],
                fight["startTime"],
                fight["endTime"],
            )

            player_metrics = build_player_metrics(
                roster,
                events,
                fight_duration_seconds,
                fight["startTime"],
                fight["endTime"],
                fight["encounterID"],
            )

            mechanics_data = calculate_mechanics(
                roster,
                events,
                fight["encounterID"],
            )

            timeline = build_timeline(
                roster,
                events,
                fight["startTime"],
                fight["encounterID"],
            )

            print_roster_table(fight.get("name", "Unknown"), roster)

            print_metrics_table(fight.get("name", "Unknown"), player_metrics)

            print_mechanics_table(
                fight.get("name", "Unknown"),
                mechanics_data,
            )

            print_cooldowns_table(
                fight.get("name", "Unknown"),
                player_metrics,
            )

            print_timeline_table(
                fight.get("name", "Unknown"),
                timeline,
            )

            benchmark_comparisons = build_benchmark_comparisons(
                report_code,
                fight,
                player_metrics,
            )

            print_benchmark_table(
                fight.get("name", "Unknown"),
                benchmark_comparisons,
            )

            issues = build_raid_issues(
                player_metrics,
                benchmark_comparisons,
            )

            print_issues_table(
                fight.get("name", "Unknown"),
                issues,
            )

            print_scorecard_table(
                fight.get("name", "Unknown"),
                player_metrics,
                issues,
                benchmark_comparisons,
            )

if __name__ == "__main__":
    main()