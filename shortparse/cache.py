import json

from datetime import datetime, timedelta, timezone
from pathlib import Path


CACHE_ROOT = Path("cache")

REPORT_CACHE_ROOT = CACHE_ROOT / "reports"
BENCHMARK_CACHE_ROOT = CACHE_ROOT / "benchmarks"

BENCHMARK_CACHE_TTL_HOURS = 12
HEALER_COUNT_CACHE_TTL_HOURS = 24

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


def is_cache_fresh(path: Path, ttl_hours: int) -> bool:
    if not path.exists():
        return False

    modified_time = datetime.fromtimestamp(
        path.stat().st_mtime,
        tz=timezone.utc,
    )

    expires_at = modified_time + timedelta(hours=ttl_hours)

    return datetime.now(timezone.utc) < expires_at


def get_cached_report_fights(report_code: str) -> dict | None:
    path = get_report_cache_dir(report_code) / "report_fights.json"
    return load_json(path)


def save_cached_report_fights(report_code: str, data: dict) -> None:
    path = get_report_cache_dir(report_code) / "report_fights.json"
    save_json(path, data)


def get_cached_fight_player_data(
    report_code: str,
    fight_id: int,
) -> dict | None:
    path = (
        get_report_cache_dir(report_code)
        / f"fight_{fight_id}_player_data.json"
    )

    return load_json(path)


def save_cached_fight_player_data(
    report_code: str,
    fight_id: int,
    data: dict,
) -> None:
    path = (
        get_report_cache_dir(report_code)
        / f"fight_{fight_id}_player_data.json"
    )

    save_json(path, data)


def get_cached_fight_events(
    report_code: str,
    fight_id: int,
) -> list[dict] | None:
    path = (
        get_report_cache_dir(report_code)
        / f"fight_{fight_id}_events.json"
    )

    return load_json(path)


def save_cached_fight_events(
    report_code: str,
    fight_id: int,
    data: list[dict],
) -> None:
    path = (
        get_report_cache_dir(report_code)
        / f"fight_{fight_id}_events.json"
    )

    save_json(path, data)


def sanitize_cache_key(value: str) -> str:
    return (
        str(value)
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("'", "")
        .replace('"', "")
    )


def get_benchmark_cache_path(
    encounter_id: int,
    difficulty: int,
    metric: str,
    class_name: str,
    spec_name: str,
) -> Path:
    filename = "_".join(
        [
            str(encounter_id),
            str(difficulty),
            sanitize_cache_key(metric),
            sanitize_cache_key(class_name),
            sanitize_cache_key(spec_name),
        ]
    )

    return BENCHMARK_CACHE_ROOT / f"{filename}.json"


def get_cached_benchmark_rankings(
    encounter_id: int,
    difficulty: int,
    metric: str,
    class_name: str,
    spec_name: str,
) -> list[dict] | None:
    path = get_benchmark_cache_path(
        encounter_id,
        difficulty,
        metric,
        class_name,
        spec_name,
    )

    if not is_cache_fresh(
        path,
        BENCHMARK_CACHE_TTL_HOURS,
    ):
        return None

    return load_json(path)


def save_cached_benchmark_rankings(
    encounter_id: int,
    difficulty: int,
    metric: str,
    class_name: str,
    spec_name: str,
    data: list[dict],
) -> None:
    path = get_benchmark_cache_path(
        encounter_id,
        difficulty,
        metric,
        class_name,
        spec_name,
    )

    save_json(path, data)

def get_healer_count_cache_path(
    report_code: str,
    fight_id: int,
) -> Path:
    filename = "_".join(
        [
            sanitize_cache_key(report_code),
            str(fight_id),
            "healer_count",
        ]
    )

    return BENCHMARK_CACHE_ROOT / "healer_counts" / f"{filename}.json"


def get_cached_healer_count(
    report_code: str,
    fight_id: int,
) -> int | None:
    path = get_healer_count_cache_path(
        report_code,
        fight_id,
    )

    if not is_cache_fresh(
        path,
        HEALER_COUNT_CACHE_TTL_HOURS,
    ):
        return None

    data = load_json(path)

    if not isinstance(data, dict):
        return None

    healer_count = data.get("healer_count")

    if healer_count is None:
        return None

    return int(healer_count)


def save_cached_healer_count(
    report_code: str,
    fight_id: int,
    healer_count: int,
) -> None:
    path = get_healer_count_cache_path(
        report_code,
        fight_id,
    )

    save_json(
        path,
        {
            "report_code": report_code,
            "fight_id": fight_id,
            "healer_count": healer_count,
        },
    )