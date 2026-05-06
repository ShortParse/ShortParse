def calculate_grade(percent: float | None) -> str:
    if percent is None:
        return "N/A"

    if percent >= 99:
        return "S"

    if percent >= 90:
        return "A"

    if percent >= 80:
        return "B"

    if percent >= 70:
        return "C"

    if percent >= 60:
        return "D"

    return "F"