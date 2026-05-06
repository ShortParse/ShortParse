import json
from pathlib import Path


CACHE_ROOT = Path("cache")
REPORT_CACHE_ROOT = CACHE_ROOT / "reports"


def get_report_cache_dir(report_code: str) -> Path:
    cache_dir = REPORT_CACHE_ROOT / report_code
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_cached_report_fights(report_code: str) -> dict | None:
    path = get_report_cache_dir(report_code) / "report_fights.json"
    return load_json(path)


def save_cached_report_fights(report_code: str, data: dict) -> None:
    path = get_report_cache_dir(report_code) / "report_fights.json"
    save_json(path, data)


def get_cached_fight_player_data(report_code: str, fight_id: int) -> dict | None:
    path = get_report_cache_dir(report_code) / f"fight_{fight_id}_player_data.json"
    return load_json(path)


def save_cached_fight_player_data(
    report_code: str,
    fight_id: int,
    data: dict,
) -> None:
    path = get_report_cache_dir(report_code) / f"fight_{fight_id}_player_data.json"
    save_json(path, data)


def get_cached_fight_events(report_code: str, fight_id: int) -> list[dict] | None:
    path = get_report_cache_dir(report_code) / f"fight_{fight_id}_events.json"
    return load_json(path)


def save_cached_fight_events(
    report_code: str,
    fight_id: int,
    data: list[dict],
) -> None:
    path = get_report_cache_dir(report_code) / f"fight_{fight_id}_events.json"
    save_json(path, data)