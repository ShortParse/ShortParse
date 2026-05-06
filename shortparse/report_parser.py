import re


def extract_report_code(url_or_code: str) -> str:
    text = url_or_code.strip()

    patterns = [
        r"warcraftlogs\.com/reports/([a-zA-Z0-9]+)",
        r"warcraftlogs\.com/report/([a-zA-Z0-9]+)",
        r"reports/([a-zA-Z0-9]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    if re.fullmatch(r"[a-zA-Z0-9]+", text):
        return text

    raise ValueError("Could not find a Warcraft Logs report code in that input.")