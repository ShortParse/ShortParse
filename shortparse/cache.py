import json
import redis

try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False

from datetime import datetime, timedelta, timezone
from pathlib import Path

from shortparse.settings import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
)

# Attempt connection to Redis with fallback verification
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD or None,
        socket_timeout=2.0,
    )
    redis_client.ping()
    HAS_REDIS = True
except Exception:
    redis_client = None
    HAS_REDIS = False


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

    if HAS_ORJSON:
        try:
            return orjson.loads(path.read_bytes())
        except Exception:
            pass

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if HAS_ORJSON:
        try:
            path.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))
            return
        except Exception:
            pass

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


def is_cache_fresh_seconds(path: Path, ttl_seconds: int) -> bool:
    if not path.exists():
        return False

    modified_time = datetime.fromtimestamp(
        path.stat().st_mtime,
        tz=timezone.utc,
    )

    expires_at = modified_time + timedelta(seconds=ttl_seconds)

    return datetime.now(timezone.utc) < expires_at


def get_cached_report_fights(report_code: str) -> dict | None:
    path = get_report_cache_dir(report_code) / "report_fights.json"
    if not path.exists():
        return None

    data = load_json(path)
    if not data:
        return None

    # If the report is completely empty (no fights yet), do not use cached result
    fights = data.get("fights") or []
    if not fights:
        return None

    # Recency check: if the last fight ended within 6 hours, it is a live/recent log.
    # Otherwise, it's an archived log and we can cache it for 24 hours (86400 seconds).
    is_recent = False
    try:
        max_end = max(f.get("endTime", 0) for f in fights)
        if max_end > 0:
            last_fight_time = datetime.fromtimestamp(max_end / 1000, tz=timezone.utc)
            if datetime.now(timezone.utc) - last_fight_time < timedelta(hours=6):
                is_recent = True
    except Exception:
        is_recent = True

    ttl = 60 if is_recent else 86400

    if not is_cache_fresh_seconds(path, ttl):
        return None

    return data


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
    if HAS_REDIS:
        try:
            key = f"shortparse:benchmark:{encounter_id}:{difficulty}:{metric}:{class_name}:{spec_name}"
            value = redis_client.get(key)
            if value is not None:
                if HAS_ORJSON:
                    return orjson.loads(value)
                return json.loads(value.decode("utf-8"))
        except Exception:
            pass

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
    if HAS_REDIS:
        try:
            key = f"shortparse:benchmark:{encounter_id}:{difficulty}:{metric}:{class_name}:{spec_name}"
            if HAS_ORJSON:
                serialized = orjson.dumps(data)
            else:
                serialized = json.dumps(data)
            # TTL: 12 hours (43200 seconds)
            redis_client.setex(key, 43200, serialized)
        except Exception:
            pass

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
    if HAS_REDIS:
        try:
            key = f"shortparse:healer_count:{report_code}:{fight_id}"
            value = redis_client.get(key)
            if value is not None:
                return int(value)
        except Exception:
            pass

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
    if HAS_REDIS:
        try:
            key = f"shortparse:healer_count:{report_code}:{fight_id}"
            # TTL: 24 hours (86400 seconds)
            redis_client.setex(key, 86400, healer_count)
        except Exception:
            pass

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