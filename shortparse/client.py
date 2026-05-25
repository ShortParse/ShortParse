import random
import requests
import threading
import time

from shortparse.auth import get_access_token
from shortparse.cache import (
    get_cached_fight_events,
    get_cached_fight_player_data,
    get_cached_report_fights,
    save_cached_fight_events,
    save_cached_fight_player_data,
    save_cached_report_fights,
)

_log_lock = threading.Lock()
_last_rate_limit_logged = 0.0

CLIENT_GRAPHQL_URL = "https://www.warcraftlogs.com/api/v2/client"
USER_GRAPHQL_URL = "https://www.warcraftlogs.com/api/v2/user"


class WarcraftLogsClient:
    def __init__(
        self,
        access_token: str | None = None,
        use_user_endpoint: bool = False,
    ):
        self.access_token = access_token or get_access_token()
        self.use_user_endpoint = use_user_endpoint
        self.graphql_url = USER_GRAPHQL_URL if use_user_endpoint else CLIENT_GRAPHQL_URL

        # Safety: do not cache private/user-token report data yet.
        self.cache_enabled = not use_user_endpoint

    def graphql(self, query: str, variables: dict | None = None) -> dict:
        global _last_rate_limit_logged

        max_retries = 5
        backoff_factor = 2.0

        for attempt in range(max_retries):
            response = requests.post(
                self.graphql_url,
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

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")

                if retry_after:
                    try:
                        sleep_time = float(retry_after)
                    except ValueError:
                        sleep_time = backoff_factor ** attempt + random.uniform(0.1, 1.0)
                else:
                    sleep_time = backoff_factor ** attempt + random.uniform(0.1, 1.0)

                with _log_lock:
                    now = time.time()
                    if now - _last_rate_limit_logged > 5.0:
                        _last_rate_limit_logged = now
                        print(
                            f"[RATE LIMIT 429] Hit 429 for WCL API. "
                            f"Retrying in {sleep_time:.2f}s... "
                            f"(Attempt {attempt + 1}/{max_retries})"
                        )

                time.sleep(sleep_time)
                continue

            response.raise_for_status()
            payload = response.json()

            if "errors" in payload:
                errors = payload["errors"]
                is_rate_limit = False

                for err in errors:
                    msg = err.get("message", "").lower()
                    if (
                        "rate limit" in msg
                        or "too many requests" in msg
                        or "points limit" in msg
                        or "throttled" in msg
                    ):
                        is_rate_limit = True
                        break

                if is_rate_limit:
                    sleep_time = backoff_factor ** attempt + random.uniform(0.1, 1.0)

                    with _log_lock:
                        now = time.time()
                        if now - _last_rate_limit_logged > 5.0:
                            _last_rate_limit_logged = now
                            print(
                                f"[RATE LIMIT GRAPHQL] GraphQL rate limit error. "
                                f"Retrying in {sleep_time:.2f}s... "
                                f"(Attempt {attempt + 1}/{max_retries})"
                            )

                    time.sleep(sleep_time)
                    continue

                raise RuntimeError(errors)

            return payload["data"]

        raise RuntimeError("Exhausted WCL API retries due to rate limit 429")

    def get_report_fights(self, report_code: str) -> dict:
        if self.cache_enabled:
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

        if self.cache_enabled:
            save_cached_report_fights(report_code, report)

        return report

    def get_fight_player_data(self, report_code: str, fight_id: int) -> dict:
        if self.cache_enabled:
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

        if self.cache_enabled:
            save_cached_fight_player_data(report_code, fight_id, report_data)

        return report_data

    def get_fight_events(
        self,
        report_code: str,
        fight_id: int,
        start_time: int,
        end_time: int,
    ) -> list[dict]:
        if self.cache_enabled:
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

        if self.cache_enabled:
            save_cached_fight_events(report_code, fight_id, all_events)

        return all_events

    def get_user_guilds(self) -> list[dict]:
        query = """
        query {
          userData {
            currentUser {
              characters {
                guilds {
                  id
                  name
                  faction {
                    id
                    name
                  }
                  server {
                    name
                    slug
                    region {
                      compactName
                    }
                  }
                }
              }
            }
          }
        }
        """
        data = self.graphql(query)
        if not data:
            return []

        user_data = data.get("userData")
        if not user_data:
            return []

        current_user = user_data.get("currentUser")
        if not current_user:
            return []

        characters = current_user.get("characters") or []

        guilds_map = {}
        for char in characters:
            if not char:
                continue
            char_guilds = char.get("guilds") or []
            for g in char_guilds:
                if not g or not g.get("id"):
                    continue
                guild_id = g["id"]
                if guild_id not in guilds_map:
                    server_data = g.get("server") or {}
                    region_data = server_data.get("region") or {}
                    guilds_map[guild_id] = {
                        "id": guild_id,
                        "name": g.get("name"),
                        "faction": g.get("faction"),
                        "server": {
                            "name": server_data.get("name"),
                            "slug": server_data.get("slug"),
                        },
                        "region": {
                            "compact": region_data.get("compactName"),
                        },
                    }

        return list(guilds_map.values())

    def get_guild_reports(self, guild_id: int, limit: int = 10) -> list[dict]:
        query = """
        query($guildID: Int, $limit: Int) {
          reportData {
            reports(guildID: $guildID, limit: $limit) {
              data {
                code
                title
                startTime
                endTime
                owner {
                  name
                }
              }
            }
          }
        }
        """
        data = self.graphql(query, {"guildID": guild_id, "limit": limit})
        if not data:
            return []

        report_data = data.get("reportData")
        if not report_data:
            return []

        reports_pagination = report_data.get("reports")
        if not reports_pagination:
            return []

        return reports_pagination.get("data") or []