import json
import math

from typing import Any


EXTRA_MARKET_LINES = ("1.5", "2.5", "3.5", "4.5", "5.5")
EXTRA_MARKET_CODES = tuple(
    f"{direction}_{line.replace('.', '_')}"
    for line in EXTRA_MARKET_LINES
    for direction in ("OVER", "UNDER")
)


def normalize_extra_markets(value: Any) -> dict[str, float]:
    """Return a validated {market_code: points} configuration."""
    if value in (None, "", {}):
        return {}

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("extra_markets must be valid JSON") from exc

    if not isinstance(value, dict):
        raise ValueError("extra_markets must be an object")

    normalized: dict[str, float] = {}
    for raw_code, raw_points in value.items():
        code = str(raw_code).upper()
        if code not in EXTRA_MARKET_CODES:
            raise ValueError(f"Unsupported extra market: {raw_code}")

        try:
            points = float(raw_points)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Points for {code} must be a valid number") from exc

        if not math.isfinite(points):
            raise ValueError(f"Points for {code} must be a finite number")

        if points < 0:
            raise ValueError(f"Points for {code} cannot be negative")

        normalized[code] = points

    return normalized


def extra_market_label(code: str) -> str:
    direction, line = code.split("_", 1)
    return f"{direction.title()} {line.replace('_', '.')}"


def is_extra_market_correct(code: str, home_score: int, away_score: int) -> bool:
    """Evaluate an over/under total-goals market against the final score."""
    direction, line = code.split("_", 1)
    threshold = float(line.replace("_", "."))
    total_goals = home_score + away_score
    return total_goals > threshold if direction == "OVER" else total_goals < threshold


def extra_market_points(match: Any, code: str) -> float:
    return float((match.extra_markets or {}).get(code, 0) or 0)


def fixed_market_points(match: Any, code: str) -> float:
    return {
        "HOME_WIN": float(match.home_win_points or 0),
        "AWAY_WIN": float(match.away_win_points or 0),
        "DRAW": float(match.draw_points or 0),
    }[code]


def market_points(match: Any, code: str) -> float:
    if code in ("HOME_WIN", "AWAY_WIN", "DRAW"):
        return fixed_market_points(match, code)
    return extra_market_points(match, code)


def is_market_allowed(match: Any, code: str) -> bool:
    if code in ("HOME_WIN", "AWAY_WIN", "DRAW"):
        return True
    return code in (match.extra_markets or {})
