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
                fightPercentage
                lastPhase
                lastPhaseAsAbsoluteIndex
                lastPhaseIsIntermission
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

    def get_fight_player_data(self, report_code: str, fight_id: int) -> dict:
        query = """
        query($code: String!, $fightIDs: [Int]) {
          reportData {
            report(code: $code) {
              playerDetails(fightIDs: $fightIDs, includeCombatantInfo: true)
              damageDone: table(dataType: DamageDone, fightIDs: $fightIDs)
              healing: table(dataType: Healing, fightIDs: $fightIDs)
              damageTaken: table(dataType: DamageTaken, fightIDs: $fightIDs)
              deaths: table(dataType: Deaths, fightIDs: $fightIDs)
            }
          }
        }
        """

        data = self.graphql(query, {"code": report_code, "fightIDs": [fight_id]})
        return data["reportData"]["report"]