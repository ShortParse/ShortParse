import requests

from shortparse.auth import get_access_token
from shortparse.cache import (
    get_cached_fight_events,
    get_cached_fight_player_data,
    get_cached_report_fights,
    save_cached_fight_events,
    save_cached_fight_player_data,
    save_cached_report_fights,
)

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
        cached = get_cached_report_fights(report_code)

        if cached is not None:
            print(f"[CACHE HIT] report fights: {report_code}")
            return cached

        print(f"[API PULL] report fights: {report_code}")

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
        report = data["reportData"]["report"]

        save_cached_report_fights(report_code, report)

        return report

    def get_fight_player_data(self, report_code: str, fight_id: int) -> dict:
        cached = get_cached_fight_player_data(report_code, fight_id)

        if cached is not None:
            print(f"[CACHE HIT] player data: {report_code} fight {fight_id}")
            return cached

        print(f"[API PULL] player data: {report_code} fight {fight_id}")

        query = """
        query($code: String!, $fightIDs: [Int]) {
          reportData {
            report(code: $code) {

              playerDetails(
                fightIDs: $fightIDs,
                includeCombatantInfo: true
              )

              damageDone: table(
                dataType: DamageDone,
                fightIDs: $fightIDs
              )

              healing: table(
                dataType: Healing,
                fightIDs: $fightIDs
              )

              damageTaken: table(
                dataType: DamageTaken,
                fightIDs: $fightIDs
              )

              deaths: table(
                dataType: Deaths,
                fightIDs: $fightIDs
              )
            }
          }
        }
        """

        data = self.graphql(
            query,
            {
                "code": report_code,
                "fightIDs": [fight_id],
            },
        )

        report_data = data["reportData"]["report"]

        save_cached_fight_player_data(report_code, fight_id, report_data)

        return report_data

    def get_fight_events(
        self,
        report_code: str,
        fight_id: int,
        start_time: int,
        end_time: int,
    ) -> list[dict]:
        cached = get_cached_fight_events(report_code, fight_id)

        if cached is not None:
            print(f"[CACHE HIT] events: {report_code} fight {fight_id}")
            return cached

        print(f"[API PULL] events: {report_code} fight {fight_id}")

        query = """
        query(
          $code: String!,
          $fightID: Int!,
          $startTime: Float!,
          $endTime: Float!
        ) {
          reportData {
            report(code: $code) {
              events(
                dataType: DamageTaken,
                  fightIDs: [$fightID],
                    startTime: $startTime,
                      endTime: $endTime
                      ) {
                data
                nextPageTimestamp
              }
            }
          }
        }
        """

        all_events = []
        next_timestamp = start_time

        while True:
            data = self.graphql(
                query,
                {
                    "code": report_code,
                    "fightID": fight_id,
                    "startTime": next_timestamp,
                    "endTime": end_time,
                },
            )

            payload = data["reportData"]["report"]["events"]

            all_events.extend(payload.get("data", []))

            next_page = payload.get("nextPageTimestamp")

            if not next_page:
                break

            next_timestamp = next_page

        save_cached_fight_events(report_code, fight_id, all_events)

        return all_events