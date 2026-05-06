from shortparse.benchmarks.models import (
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


def calculate_average_baseline(
    benchmark: BenchmarkResult,
) -> float | None:
    values = []

    if benchmark.top_1:
        values.append(benchmark.top_1.value)

    if benchmark.top_5:
        values.append(benchmark.top_5.value)

    if benchmark.top_10:
        values.append(benchmark.top_10.value)

    if not values:
        return None

    return sum(values) / len(values)


def compare_player_to_benchmark(
    request: BenchmarkRequest,
    player_value: float,
    benchmark: BenchmarkResult,
) -> PlayerBenchmarkComparison:

    top_1_value = benchmark.top_1.value if benchmark.top_1 else None
    top_5_value = benchmark.top_5.value if benchmark.top_5 else None
    top_10_value = benchmark.top_10.value if benchmark.top_10 else None

    average_baseline = calculate_average_baseline(benchmark)

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
        percent_of_average=calculate_percent(
            player_value,
            average_baseline,
        ),
    )