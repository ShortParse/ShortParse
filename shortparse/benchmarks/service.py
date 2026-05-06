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

    def build_entry(
        self,
        rank: int,
        ranking: dict,
    ) -> BenchmarkEntry:
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
        )

    def get_benchmark_result(
        self,
        request: BenchmarkRequest,
    ) -> BenchmarkResult:
        rankings = self.fetch_character_rankings(request)

        top_1 = self.build_entry(1, rankings[0]) if len(rankings) >= 1 else None
        top_5 = self.build_entry(5, rankings[4]) if len(rankings) >= 5 else None
        top_10 = self.build_entry(10, rankings[9]) if len(rankings) >= 10 else None

        return BenchmarkResult(
            request=request,
            top_1=top_1,
            top_5=top_5,
            top_10=top_10,
        )