def calculate_grade(percent: float | None) -> str:
    if percent is None:
        return "N/A"

    if percent >= 90:
        return "S"

    if percent >= 80:
        return "A"

    if percent >= 70:
        return "B"

    if percent >= 55:
        return "C"

    if percent >= 40:
        return "D"

    return "F"