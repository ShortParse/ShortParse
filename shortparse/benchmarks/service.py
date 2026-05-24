from dataclasses import dataclass

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


@dataclass(frozen=True)
class BenchmarkFilterTier:
    name: str
    item_level_tolerance: int | None
    fight_duration_tolerance_seconds: int | None
    raid_size_tolerance: int | None
    healer_count_tolerance: int | None


FILTER_TIERS = [
    BenchmarkFilterTier("Strict", 5, 30, 2, 1),
    BenchmarkFilterTier("Relaxed", 8, 60, 4, 2),
    BenchmarkFilterTier("Broad", 12, None, None, 2),
    BenchmarkFilterTier("Emergency", None, None, None, None),
]


class BenchmarkService:
    def __init__(self):
        self.client = WarcraftLogsClient()

    def filter_rankings_for_request(
        self,
        request: BenchmarkRequest,
        rankings: list[dict],
        tier: BenchmarkFilterTier,
    ) -> list[dict]:

        filtered = []

        for ranking in rankings:
            item_level = ranking.get("bracketData")
            duration = ranking.get("duration")
            size = ranking.get("size")

            if item_level is None or duration is None:
                continue

            if tier.item_level_tolerance is not None:
                min_item_level = request.item_level - tier.item_level_tolerance
                max_item_level = request.item_level + tier.item_level_tolerance

                if not min_item_level <= item_level <= max_item_level:
                    continue

            if (
                request.kill
                and tier.fight_duration_tolerance_seconds is not None
            ):
                min_duration_ms = (
                    request.fight_duration_seconds
                    - tier.fight_duration_tolerance_seconds
                ) * 1000

                max_duration_ms = (
                    request.fight_duration_seconds
                    + tier.fight_duration_tolerance_seconds
                ) * 1000

                if not min_duration_ms <= duration <= max_duration_ms:
                    continue

            if (
                request.metric == "hps"
                and request.raid_size is not None
                and tier.raid_size_tolerance is not None
            ):
                if size is None:
                    continue

                min_size = request.raid_size - tier.raid_size_tolerance
                max_size = request.raid_size + tier.raid_size_tolerance

                if not min_size <= size <= max_size:
                    continue

            if (
                request.metric == "hps"
                and request.healer_count is not None
                and tier.healer_count_tolerance is not None
            ):
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

                if benchmark_healer_count < 0:
                    continue

                if abs(
                    benchmark_healer_count
                    - request.healer_count
                ) > tier.healer_count_tolerance:
                    continue

            filtered.append(ranking)

        return filtered

    def filter_rankings_with_fallbacks(
        self,
        request: BenchmarkRequest,
        rankings: list[dict],
    ) -> tuple[list[dict], str, bool]:

        best_available = []

        for tier in FILTER_TIERS:
            filtered = self.filter_rankings_for_request(
                request,
                rankings,
                tier,
            )

            if len(filtered) > len(best_available):
                best_available = filtered

            if len(filtered) >= 10:
                print(
                    "[BENCHMARK TIER]",
                    request.player_name,
                    request.metric,
                    tier.name,
                    f"{len(filtered)} matches",
                )

                return (
                    filtered,
                    tier.name,
                    tier.name != "Strict",
                )

        print(
            "[BENCHMARK TIER]",
            request.player_name,
            request.metric,
            "BestAvailable",
            f"{len(best_available)} matches",
        )

        return (
            best_available,
            "BestAvailable",
            True,
        )

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
        
        # WCL API does not reliably filter spec/class correctly.
        # Force strict filtering locally.
        rankings = [
            ranking
            for ranking in rankings
            if (
                ranking.get("class") == request.class_name
                and ranking.get("spec") == request.spec_name
            )
        ]

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

        try:
            data = self.client.graphql(query)

        except RuntimeError as error:
            print(
                "[HEALER COUNT SKIP]",
                report_code,
                fight_id,
                error,
            )

            return -1

        player_details = (
            data["reportData"]
            ["report"]
            ["playerDetails"]
        )

        details_data = player_details.get("data", {})
        details = details_data.get("playerDetails", {})

        if isinstance(details, dict):
            healers = details.get("healers", [])

        elif isinstance(details, list):
            healers = [
                player
                for player in details
                if (
                    player.get("type") == "Healer"
                    or player.get("role") == "Healer"
                )
            ]

        else:
            healers = []

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

        (
            rankings,
            filter_tier_used,
            used_relaxed_filters,
        ) = self.filter_rankings_with_fallbacks(
            request,
            rankings,
        )

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
            filter_tier_used=filter_tier_used,
            filter_match_count=len(rankings),
            used_relaxed_filters=used_relaxed_filters,
        )