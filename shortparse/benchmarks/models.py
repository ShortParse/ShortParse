from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkRequest:
    report_code: str
    fight_id: int
    encounter_id: int
    difficulty: int
    raid_size: int | None
    fight_duration_seconds: float
    player_name: str
    class_name: str
    spec_name: str
    role: str
    item_level: int
    metric: str  # "dps" or "hps"


@dataclass(frozen=True)
class BenchmarkEntry:
    rank: int
    player_name: str
    class_name: str
    spec_name: str
    item_level: int | None
    fight_duration_seconds: float | None
    value: float


@dataclass(frozen=True)
class BenchmarkResult:
    request: BenchmarkRequest
    top_1: BenchmarkEntry | None
    top_5: BenchmarkEntry | None
    top_10: BenchmarkEntry | None
    average_baseline: float | None

    def best_available_baseline(self) -> BenchmarkEntry | None:
        return self.top_10 or self.top_5 or self.top_1


@dataclass(frozen=True)
class PlayerBenchmarkComparison:
    player_name: str
    metric: str
    player_value: float
    benchmark: BenchmarkResult
    percent_of_top_1: float | None
    percent_of_top_5: float | None
    percent_of_top_10: float | None
    percent_of_average: float | None