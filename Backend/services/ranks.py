# ==========================================
# RANK SYSTEM
# ==========================================
# Ranks are driven entirely by a user's total points. Each tier
# below is checked from highest to lowest so a user's rank
# always matches the highest threshold they've crossed.
#
# Bronze/Silver/Gold render as a colored shield icon on the
# frontend (icon_type = "shield"). Platinum and above render as
# an emoji (icon_type = "emoji").

RANKS = [

    {
        "key": "BRONZE",
        "label": "Bronze",
        "min_points": 0,
        "icon_type": "shield",
        "icon": "shield",
        "color": "#CD7F32"
    },

    {
        "key": "SILVER",
        "label": "Silver",
        "min_points": 200,
        "icon_type": "shield",
        "icon": "shield",
        "color": "#C0C0C0"
    },

    {
        "key": "GOLD",
        "label": "Gold",
        "min_points": 500,
        "icon_type": "shield",
        "icon": "shield",
        "color": "#FFD700"
    },

    {
        "key": "PLATINUM",
        "label": "Platinum",
        "min_points": 1000,
        "icon_type": "emoji",
        "icon": "💎",
        "color": "#7FDBFF"
    },

    {
        "key": "DIAMOND",
        "label": "Diamond",
        "min_points": 1800,
        "icon_type": "emoji",
        "icon": "👑",
        "color": "#B9E3FF"
    },

    {
        "key": "MASTER",
        "label": "Master",
        "min_points": 2800,
        "icon_type": "emoji",
        "icon": "🔥",
        "color": "#FF7A45"
    },

    {
        "key": "GRANDMASTER",
        "label": "Grandmaster",
        "min_points": 4000,
        "icon_type": "emoji",
        "icon": "🌟",
        "color": "#C77DFF"
    },

    {
        "key": "LEGEND",
        "label": "Legend",
        "min_points": 6000,
        "icon_type": "emoji",
        "icon": "🏆",
        "color": "#FFD166"
    },

]


def get_rank_info(points: int):
    """
    Returns the full metadata dict (key, label, min_points,
    icon_type, icon, color) for the tier a given points total
    falls into.
    """

    points = points or 0

    current = RANKS[0]

    for tier in RANKS:

        if points >= tier["min_points"]:
            current = tier

        else:
            break

    return current


def get_next_rank_info(points: int):
    """
    Returns the metadata dict for the NEXT tier up, or None if
    the user is already at the highest rank (Legend).
    """

    points = points or 0

    current = get_rank_info(points)

    current_index = RANKS.index(current)

    if current_index + 1 >= len(RANKS):
        return None

    return RANKS[current_index + 1]


def get_rank(points: int) -> str:
    """
    Backwards-compatible helper — returns just the rank key
    (e.g. "BRONZE", "GOLD", "LEGEND") for a given points total.
    """

    return get_rank_info(points)["key"]


def get_rank_progress(points: int):
    """
    Returns progress info toward the next rank, useful for
    rendering a progress bar on the profile page.
    """

    points = points or 0

    current = get_rank_info(points)
    nxt = get_next_rank_info(points)

    if not nxt:

        return {
            "current": current["key"],
            "next": None,
            "points_to_next": 0,
            "progress_percent": 100
        }

    span = nxt["min_points"] - current["min_points"]
    into_tier = points - current["min_points"]

    percent = int(min(100, max(0, (into_tier / span) * 100))) if span else 100

    return {
        "current": current["key"],
        "next": nxt["key"],
        "points_to_next": max(0, nxt["min_points"] - points),
        "progress_percent": percent
    }
