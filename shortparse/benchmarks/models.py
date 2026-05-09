from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkRequest:
    report_code: str
    fight_id: int
    encounter_id: int
    difficulty: int
    kill: bool
    raid_size: int | None
    healer_count: int | None
    fight_duration_seconds: float
    player_name: str
    source_id: int | None
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
    report_code: str | None = None
    fight_id: int | None = None
    compare_url: str | None = None


@dataclass(frozen=True)
class BenchmarkResult:
    request: BenchmarkRequest
    top_1: BenchmarkEntry | None
    top_5: BenchmarkEntry | None
    top_10: BenchmarkEntry | None
    average_baseline: float | None
    filter_tier_used: str
    filter_match_count: int
    used_relaxed_filters: bool

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
    grade: str
    used_relaxed_filters: bool
    filter_tier_used: str
    filter_match_count: int