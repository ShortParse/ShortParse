ITEM_LEVEL_TOLERANCE = 5
FIGHT_DURATION_TOLERANCE_SECONDS = 30

from shortparse.benchmarks.models import (
    BenchmarkEntry,
    BenchmarkRequest,
    BenchmarkResult,
)

from shortparse.cache import (
    get_cached_benchmark_rankings,
    save_cached_benchmark_rankings,
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

            if item_level is None or duration is None:
                continue

            if not min_item_level <= item_level <= max_item_level:
                continue

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

        return (
            "https://www.warcraftlogs.com/reports/compare/"
            f"{request.report_code}/{benchmark_report_code}"
            f"?fight={request.fight_id}%2C{benchmark_fight_id}"
            f"&type={compare_type}"
            f"&source={request.player_name}%2C{benchmark_player_name}"
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

        # Muted output of rank comparison links.
        # if rankings:
        #     print(rankings[0])

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