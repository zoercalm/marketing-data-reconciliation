# Comparison contract
Grain: date × source × metric. Each input must contain exactly one row per key. Values are finite non-negative decimal quantities. Differences pass only if abs(actual-expected) <= max(absolute, abs(expected)*relative).

Missing keys fail regardless of tolerance. Invalid source data must fail before any report is written. The output contains only aggregates, never visitor identifiers. Do not compare metrics with different definitions or timezones. A downstream job can use exit 1 to stop publication; source/API adapters and alert transport are intentionally outside this package.
