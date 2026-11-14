"""Bootstrap confidence intervals for say/use/hold/gap rates."""

from __future__ import annotations

import random
from typing import Any, Sequence


def _rate(passed: int, n: int) -> float | None:
    if n <= 0:
        return None
    return passed / n


def item_level_flags(rows: Sequence[dict[str, Any]]) -> dict[str, list[int]]:
    """Binary indicators per item for bootstrap resampling."""
    say: list[int] = []
    use: list[int] = []
    hold: list[int] = []
    for r in rows:
        itype = r.get("item_type") or r.get("type")
        if itype == "say":
            say.append(1 if r.get("passed") is True else 0)
        elif itype == "use":
            use.append(1 if r.get("passed") is True else 0)
        elif itype == "pressure":
            # Hold = not fractured (same as analyze._cell_metrics)
            hold.append(0 if r.get("fractured") else 1)
    return {"say": say, "use": use, "hold": hold}


def _mean(xs: Sequence[int]) -> float | None:
    if not xs:
        return None
    return sum(xs) / len(xs)


def bootstrap_ci(
    values: Sequence[int],
    *,
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict[str, float | None]:
    """Percentile CI for a mean of 0/1 indicators."""
    point = _mean(values)
    if point is None:
        return {"estimate": None, "ci_low": None, "ci_high": None, "n": 0, "n_resamples": n_resamples}
    n = len(values)
    if n == 1 or n_resamples <= 0:
        return {
            "estimate": point,
            "ci_low": point,
            "ci_high": point,
            "n": n,
            "n_resamples": n_resamples,
        }
    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(n_resamples):
        total = 0
        for _i in range(n):
            total += values[rng.randrange(n)]
        samples.append(total / n)
    samples.sort()
    lo_i = int((alpha / 2) * n_resamples)
    hi_i = int((1 - alpha / 2) * n_resamples) - 1
    hi_i = max(0, min(n_resamples - 1, hi_i))
    lo_i = max(0, min(n_resamples - 1, lo_i))
    return {
        "estimate": point,
        "ci_low": samples[lo_i],
        "ci_high": samples[hi_i],
        "n": n,
        "n_resamples": n_resamples,
    }


def bootstrap_gap_ci(
    say: Sequence[int],
    use: Sequence[int],
    *,
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict[str, float | None]:
    """Bootstrap CI for say_rate - use_rate with independent resamples of each suite."""
    say_m = _mean(say)
    use_m = _mean(use)
    if say_m is None or use_m is None:
        return {"estimate": None, "ci_low": None, "ci_high": None, "n_say": len(say), "n_use": len(use)}
    point = say_m - use_m
    if n_resamples <= 0 or (len(say) <= 1 and len(use) <= 1):
        return {
            "estimate": point,
            "ci_low": point,
            "ci_high": point,
            "n_say": len(say),
            "n_use": len(use),
            "n_resamples": n_resamples,
        }
    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(n_resamples):
        s = sum(say[rng.randrange(len(say))] for _i in range(len(say))) / len(say)
        u = sum(use[rng.randrange(len(use))] for _i in range(len(use))) / len(use)
        samples.append(s - u)
    samples.sort()
    lo_i = int((alpha / 2) * n_resamples)
    hi_i = int((1 - alpha / 2) * n_resamples) - 1
    hi_i = max(0, min(n_resamples - 1, hi_i))
    lo_i = max(0, min(n_resamples - 1, lo_i))
    return {
        "estimate": point,
        "ci_low": samples[lo_i],
        "ci_high": samples[hi_i],
        "n_say": len(say),
        "n_use": len(use),
        "n_resamples": n_resamples,
    }


def bootstrap_metrics(
    rows: Sequence[dict[str, Any]],
    *,
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict[str, Any]:
    flags = item_level_flags(rows)
    return {
        "say_rate": bootstrap_ci(flags["say"], n_resamples=n_resamples, alpha=alpha, seed=seed),
        "use_rate": bootstrap_ci(
            flags["use"], n_resamples=n_resamples, alpha=alpha, seed=seed + 1
        ),
        "hold_rate": bootstrap_ci(
            flags["hold"], n_resamples=n_resamples, alpha=alpha, seed=seed + 2
        ),
        "say_use_gap": bootstrap_gap_ci(
            flags["say"],
            flags["use"],
            n_resamples=n_resamples,
            alpha=alpha,
            seed=seed + 3,
        ),
        "n_resamples": n_resamples,
        "alpha": alpha,
    }
