import requests

from shortparse.auth import get_access_token

GRAPHQL_URL = "https://www.warcraftlogs.com/api/v2/client"


class WarcraftLogsClient:
    def __init__(self):
        self.access_token = get_access_token()

    def graphql(self, query: str, variables: dict | None = None) -> dict:
        response = requests.post(
            GRAPHQL_URL,
            json={
                "query": query,
                "variables": variables or {},
            },
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            timeout=60,
        )

        response.raise_for_status()
        payload = response.json()

        if "errors" in payload:
            raise RuntimeError(payload["errors"])

        return payload["data"]

    def get_report_fights(self, report_code: str) -> dict:
        query = """
        query($code: String!) {
          reportData {
            report(code: $code) {
              title
              fights {
                id
                name
                encounterID
                kill
                bossPercentage
                difficulty
                startTime
                endTime
                inProgress
              }
            }
          }
          rateLimitData {
            limitPerHour
            pointsSpentThisHour
            pointsResetIn
          }
        }
        """

        data = self.graphql(query, {"code": report_code})
        return data["reportData"]["report"]