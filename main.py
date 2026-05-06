from rich.console import Console
from rich.table import Table

from shortparse.client import WarcraftLogsClient
from shortparse.players import build_roster_from_fight_data
from shortparse.report_parser import extract_report_code
from shortparse.selector import select_best_boss_encounters

console = Console()


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
    table.add_column("Deaths")

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
            str(player["deaths"]),
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
            print_roster_table(fight.get("name", "Unknown"), roster)


if __name__ == "__main__":
    main()