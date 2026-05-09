ITEM_LEVEL_TOLERANCE = 5
RAID_SIZE_TOLERANCE = 2
FIGHT_DURATION_TOLERANCE_SECONDS = 30

from shortparse.benchmarks.models import (
    BenchmarkEntry,
    BenchmarkRequest,
    BenchmarkResult,
)

from shortparse.cache import (
    get_cached_benchmark_rankings,
    save_cached_benchmark_rankings,
    get_cached_healer_count,
    save_cached_healer_count,
)

from shortparse.client import WarcraftLogsClient


class BenchmarkService:
    def __init__(self):
        self.client = WarcraftLogsClient()

    def filter_rankings_for_request(
        self,
        request: BenchmarkRequest,
        rankings: list[dict],
    ) -> list[dict]:

        filtered = []

        min_item_level = request.item_level - ITEM_LEVEL_TOLERANCE
        max_item_level = request.item_level + ITEM_LEVEL_TOLERANCE

        min_duration_ms = (
            request.fight_duration_seconds - FIGHT_DURATION_TOLERANCE_SECONDS
        ) * 1000

        max_duration_ms = (
            request.fight_duration_seconds + FIGHT_DURATION_TOLERANCE_SECONDS
        ) * 1000

        for ranking in rankings:
            item_level = ranking.get("bracketData")
            duration = ranking.get("duration")
            size = ranking.get("size")

            if item_level is None or duration is None:
                continue

            if request.raid_size is not None:
                if size is None:
                    continue

                min_size = request.raid_size - RAID_SIZE_TOLERANCE
                max_size = request.raid_size + RAID_SIZE_TOLERANCE

                if not min_size <= size <= max_size:
                    continue

            if request.metric == "hps":
                if request.healer_count is not None:
                    report = ranking.get("report", {})

                    report_code = report.get("code")
                    fight_id = report.get("fightID")

                    if not report_code or not fight_id:
                        continue

                    benchmark_healer_count = (
                        self.get_healer_count_for_report_fight(
                            report_code,
                            fight_id,
                        )
                    )

                    if abs(
                            benchmark_healer_count
                            - request.healer_count
                    ) > 1:
                        continue

            if not min_item_level <= item_level <= max_item_level:
                continue

            if request.kill:
                if not min_duration_ms <= duration <= max_duration_ms:
                    continue

            filtered.append(ranking)

        return filtered

    def fetch_character_rankings(
        self,
        request: BenchmarkRequest,
    ) -> list[dict]:

        cached = get_cached_benchmark_rankings(
            encounter_id=request.encounter_id,
            difficulty=request.difficulty,
            metric=request.metric,
            class_name=request.class_name,
            spec_name=request.spec_name,
        )

        if cached is not None:
            print(
                "[CACHE HIT] benchmark:",
                request.encounter_id,
                request.metric,
                request.class_name,
                request.spec_name,
            )

            return cached

        print(
            "[CACHE MISS] benchmark:",
            request.encounter_id,
            request.metric,
            request.class_name,
            request.spec_name,
        )

        query = f"""
        query {{
          worldData {{
            encounter(id: {request.encounter_id}) {{
              characterRankings(
                difficulty: {request.difficulty}
                metric: {request.metric}
                className: "{request.class_name}"
                specName: "{request.spec_name}"
              )
            }}
          }}
        }}
        """

        data = self.client.graphql(query)

        payload = (
            data["worldData"]
            ["encounter"]
            ["characterRankings"]
        )

        rankings = payload.get("rankings", [])

        save_cached_benchmark_rankings(
            encounter_id=request.encounter_id,
            difficulty=request.difficulty,
            metric=request.metric,
            class_name=request.class_name,
            spec_name=request.spec_name,
            data=rankings,
        )

        return rankings

    def get_healer_count_for_report_fight(
            self,
            report_code: str,
            fight_id: int,
    ) -> int:

        cached = get_cached_healer_count(report_code, fight_id)

        if cached is not None:
            return cached

        query = f"""
        query {{
          reportData {{
            report(code: "{report_code}") {{
              playerDetails(
                fightIDs: [{fight_id}]
              )
            }}
          }}
        }}
        """

        data = self.client.graphql(query)

        player_details = (
            data["reportData"]
            ["report"]
            ["playerDetails"]
        )

        healers = (
            player_details
            .get("data", {})
            .get("playerDetails", {})
            .get("healers", [])
        )

        healer_count = len(healers)

        save_cached_healer_count(
            report_code,
            fight_id,
            healer_count,
        )

        return healer_count

    def build_compare_url(
        self,
        request: BenchmarkRequest,
        ranking: dict,
    ) -> str | None:

        report = ranking.get("report", {})

        benchmark_report_code = report.get("code")
        benchmark_fight_id = report.get("fightID")
        benchmark_player_name = ranking.get("name")

        if not benchmark_report_code:
            return None

        if not benchmark_fight_id:
            return None

        if not benchmark_player_name:
            return None

        compare_type = (
            "healing"
            if request.metric == "hps"
            else "damage-done"
        )

        if not request.source_id:
            return None

        return (
            "https://www.warcraftlogs.com/reports/compare/"
            f"{request.report_code}/{benchmark_report_code}"
            f"?fight={request.fight_id}%2C{benchmark_fight_id}"
            f"&type={compare_type}"
            f"&source={request.source_id}%2C{benchmark_player_name}"
        )

    def build_entry(
        self,
        request: BenchmarkRequest,
        rank: int,
        ranking: dict,
    ) -> BenchmarkEntry:

        report = ranking.get("report", {})

        return BenchmarkEntry(
            rank=rank,
            player_name=ranking.get("name", "Unknown"),
            class_name=ranking.get("class", "Unknown"),
            spec_name=ranking.get("spec", "Unknown"),
            item_level=ranking.get("bracketData"),
            fight_duration_seconds=(
                ranking.get("duration", 0) / 1000
                if ranking.get("duration") is not None
                else None
            ),
            value=float(ranking.get("amount") or 0),
            report_code=report.get("code"),
            fight_id=report.get("fightID"),
            compare_url=self.build_compare_url(
                request,
                ranking,
            ),
        )

    def get_benchmark_result(
        self,
        request: BenchmarkRequest,
    ) -> BenchmarkResult:

        rankings = self.fetch_character_rankings(request)
        rankings = self.filter_rankings_for_request(request, rankings)

        top_1 = (
            self.build_entry(request, 1, rankings[0])
            if len(rankings) >= 1
            else None
        )

        top_5 = (
            self.build_entry(request, 5, rankings[4])
            if len(rankings) >= 5
            else None
        )

        top_10 = (
            self.build_entry(request, 10, rankings[9])
            if len(rankings) >= 10
            else None
        )

        average_values = [
            entry.value
            for entry in [top_1, top_5, top_10]
            if entry is not None
        ]

        average_baseline = (
            sum(average_values) / len(average_values)
            if average_values
            else None
        )

        return BenchmarkResult(
            request=request,
            top_1=top_1,
            top_5=top_5,
            top_10=top_10,
            average_baseline=average_baseline,
        )