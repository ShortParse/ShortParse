import json
from pathlib import Path


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

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            analysis,
            file,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    return path