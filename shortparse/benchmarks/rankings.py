from shortparse.benchmarks.models import (
    BenchmarkEntry,
    BenchmarkRequest,
    BenchmarkResult,
    PlayerBenchmarkComparison,
)


def calculate_percent(
    player_value: float,
    benchmark_value: float | None,
) -> float | None:
    if benchmark_value is None:
        return None

    if benchmark_value <= 0:
        return None

    return round(
        (player_value / benchmark_value) * 100,
        2,
    )


def build_placeholder_benchmark_result(
    request: BenchmarkRequest,
) -> BenchmarkResult:
    """
    Temporary local placeholder.

    This lets us wire the benchmark system into ShortParse before
    we finalize the Warcraft Logs rankings API query.
    """

    return BenchmarkResult(
        request=request,
        top_1=None,
        top_5=None,
        top_10=None,
    )


def compare_player_to_benchmark(
    request: BenchmarkRequest,
    player_value: float,
    benchmark: BenchmarkResult,
) -> PlayerBenchmarkComparison:

    top_1_value = benchmark.top_1.value if benchmark.top_1 else None
    top_5_value = benchmark.top_5.value if benchmark.top_5 else None
    top_10_value = benchmark.top_10.value if benchmark.top_10 else None

    return PlayerBenchmarkComparison(
        player_name=request.player_name,
        metric=request.metric,
        player_value=player_value,
        benchmark=benchmark,
        percent_of_top_1=calculate_percent(
            player_value,
            top_1_value,
        ),
        percent_of_top_5=calculate_percent(
            player_value,
            top_5_value,
        ),
        percent_of_top_10=calculate_percent(
            player_value,
            top_10_value,
        ),
    )


def build_placeholder_comparison(
    request: BenchmarkRequest,
    player_value: float,
) -> PlayerBenchmarkComparison:
    benchmark = build_placeholder_benchmark_result(request)

    return compare_player_to_benchmark(
        request,
        player_value,
        benchmark,
    )