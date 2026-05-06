from rich.console import Console
from rich.table import Table

from shortparse.client import WarcraftLogsClient
from shortparse.report_parser import extract_report_code
from shortparse.selector import select_best_boss_encounters

console = Console()


def main():
    url = input("Paste Warcraft Logs report URL: ").strip()
    report_code = extract_report_code(url)

    client = WarcraftLogsClient()
    report = client.get_report_fights(report_code)

    selected = select_best_boss_encounters(report["fights"])

    console.print(f"\n[bold cyan]ShortParse Report:[/bold cyan] {report['title']}\n")

    for raid_name, fights in selected.items():
        console.print(f"[bold yellow]{raid_name}[/bold yellow]")

        table = Table(show_header=True, header_style="bold")
        table.add_column("Boss")
        table.add_column("Fight ID")
        table.add_column("Result")
        table.add_column("Boss HP Left")
        table.add_column("Duration")

        for fight in fights:
            duration_seconds = int((fight["endTime"] - fight["startTime"]) / 1000)
            minutes = duration_seconds // 60
            seconds = duration_seconds % 60

            result = "KILL" if fight.get("kill") else "BEST WIPE"
            boss_hp = fight.get("bossPercentage")

            if boss_hp is None:
                boss_hp_text = "Unknown"
            else:
                boss_hp_text = f"{boss_hp:.2f}%"

            table.add_row(
                fight.get("name", "Unknown"),
                str(fight.get("id")),
                result,
                boss_hp_text,
                f"{minutes}:{seconds:02d}",
            )

        console.print(table)
        console.print()


if __name__ == "__main__":
    main()