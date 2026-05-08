from shortparse.benchmarks.models import BenchmarkRequest
from shortparse.benchmarks.rankings import compare_player_to_benchmark
from shortparse.benchmarks.service import BenchmarkService


def get_metric_for_role(role: str) -> str:
    if role == "Healer":
        return "hps"

    return "dps"


def build_benchmark_requests(
    report_code: str,
    fight: dict,
    player_metrics: dict,
) -> list[BenchmarkRequest]:

    requests = []

    fight_duration_seconds = (
        fight["endTime"] - fight["startTime"]
    ) / 1000

    for player_name, metric_data in player_metrics.items():
        identity = metric_data["identity"]
        role = identity["role"]
        metric = get_metric_for_role(role)

        requests.append(
            BenchmarkRequest(
                report_code=report_code,
                fight_id=fight["id"],
                encounter_id=fight["encounterID"],
                difficulty=fight["difficulty"],
                raid_size=None,
                fight_duration_seconds=fight_duration_seconds,
                player_name=player_name,
                source_id=identity.get("actor_id"),
                class_name=identity["class"],
                spec_name=identity["spec"],
                role=role,
                item_level=identity["item_level"],
                metric=metric,
            )
        )

    return requests


def build_benchmark_comparisons(
    report_code: str,
    fight: dict,
    player_metrics: dict,
) -> dict:

    comparisons = {}
    service = BenchmarkService()

    requests = build_benchmark_requests(
        report_code,
        fight,
        player_metrics,
    )

    for request in requests:
        metric_data = player_metrics[request.player_name]
        performance = metric_data["performance"]

        player_value = performance.get(request.metric, 0)
        benchmark = service.get_benchmark_result(request)

        comparisons[request.player_name] = compare_player_to_benchmark(
            request,
            player_value,
            benchmark,
        )

    return comparisons