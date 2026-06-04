import orjson
from pathlib import Path

from shortparse.reports.serializers import serialize_analysis


def ensure_parent_directory(path: Path) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


def save_analysis_json(
    analysis: dict,
    output_path: str,
) -> Path:

    path = Path(output_path)

    ensure_parent_directory(path)

    serialized = serialize_analysis(analysis)

    # Use high-performance orjson with 2 spaces indent and support for non-string dictionary keys
    data = orjson.dumps(
        serialized,
        option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS,
    )

    with open(path, "wb") as file:
        file.write(data)

    return path