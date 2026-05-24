import concurrent.futures

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

    healer_count = sum(
        1
        for metric_data in player_metrics.values()
        if metric_data["identity"]["role"] == "Healer"
    )

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
                kill=fight["kill"],
                raid_size=len(player_metrics),
                healer_count=healer_count,
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
    progress_callback=None,
) -> dict:

    comparisons = {}
    service = BenchmarkService()

    requests = build_benchmark_requests(
        report_code,
        fight,
        player_metrics,
    )

    completed_count = 0

    def process_request(request):
        nonlocal completed_count
        benchmark = service.get_benchmark_result(request)
        completed_count += 1
        if progress_callback:
            progress_callback(
                (
                    f"benchmarking "
                    f"{request.player_name} "
                    f"({completed_count}/{len(requests)})..."
                )
            )
        return request.player_name, benchmark

    # Execute requests concurrently using a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_request, req) for req in requests]
        
        results = {}
        for future in concurrent.futures.as_completed(futures):
            player_name, benchmark = future.result()
            results[player_name] = benchmark

    # Build final comparisons dictionary preserving order of requests
    for request in requests:
        player_name = request.player_name
        metric_data = player_metrics[player_name]
        performance = metric_data["performance"]

        player_value = performance.get(request.metric, 0)
        benchmark = results[player_name]

        comparisons[player_name] = compare_player_to_benchmark(
            request,
            player_value,
            benchmark,
        )

    return comparisons