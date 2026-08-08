import logging

from sqlalchemy import text


logger = logging.getLogger("predix.seed")


# ==========================================
# BADGE CATALOG
# ==========================================
# Single source of truth for the badges that should exist in the
# `badges` table. Runs automatically on every app startup (see
# main.py) so a fresh — or already-existing — Supabase database
# always ends up with these rows, without anyone having to run
# SQL by hand.

BADGE_CATALOG = [

    {
        "name": "First Prediction",
        "description": "Make your first prediction.",
        "icon": "🎯",
        "rarity": "Common"
    },

    {
        "name": "First Win",
        "description": "Get your first correct prediction.",
        "icon": "🏆",
        "rarity": "Common"
    },

    {
        "name": "Hot Streak",
        "description": "Win 5 predictions in a row.",
        "icon": "🔥",
        "rarity": "Rare"
    },

    {
        "name": "Prediction Master",
        "description": "Reach 100 correct predictions.",
        "icon": "🧠",
        "rarity": "Epic"
    },

    {
        "name": "Bronze Predictor",
        "description": "Reach the Bronze rank.",
        "icon": "🥉",
        "rarity": "Common"
    },

    {
        "name": "Silver Predictor",
        "description": "Reach the Silver rank.",
        "icon": "🥈",
        "rarity": "Uncommon"
    },

    {
        "name": "Gold Predictor",
        "description": "Reach the Gold rank.",
        "icon": "🥇",
        "rarity": "Rare"
    },

    {
        "name": "Elite Predictor",
        "description": "Reach the Elite rank.",
        "icon": "💎",
        "rarity": "Epic"
    },

    {
        "name": "Legend",
        "description": "Reach 1000 total points.",
        "icon": "👑",
        "rarity": "Legendary"
    },

]


def ensure_badge_schema(engine):
    """
    Adds the `rarity` column to an already-existing `badges`
    table if it isn't there yet. Base.metadata.create_all() only
    creates brand-new tables — it never alters existing ones —
    so on a database that already had a `badges` table (e.g. an
    existing Supabase project) this is what actually adds the
    new column.
    """

    try:

        with engine.begin() as conn:

            conn.execute(text(
                """
                ALTER TABLE badges
                ADD COLUMN IF NOT EXISTS rarity VARCHAR DEFAULT 'Common'
                """
            ))

        logger.info("[seed] badges.rarity column present/verified")

    except Exception as exc:

        # Never let a schema hiccup take the whole API down — log
        # it loudly instead so it shows up in the server logs, and
        # let seed_badges() (which also needs `rarity`) surface the
        # real problem if the column genuinely isn't there.
        logger.error(f"[seed] ensure_badge_schema failed: {exc}")


def seed_badges(db):
    """
    Upserts every badge in BADGE_CATALOG by name: inserts it if
    missing, and refreshes description/icon/rarity if it already
    exists (so editing the catalog above is enough to update the
    live data too). Existing user_badges (who already earned a
    badge) are untouched either way.

    Returns the number of badges inserted/updated so callers (the
    startup hook, or the manual /admin/badges/reseed endpoint) can
    report exactly what happened instead of it being a silent
    no-op.
    """

    from models import Badge

    inserted = 0
    updated = 0

    try:

        for entry in BADGE_CATALOG:

            badge = db.query(Badge).filter(
                Badge.name == entry["name"]
            ).first()

            if badge:

                badge.description = entry["description"]
                badge.icon = entry["icon"]
                badge.rarity = entry["rarity"]

                updated += 1

            else:

                db.add(Badge(
                    name=entry["name"],
                    description=entry["description"],
                    icon=entry["icon"],
                    rarity=entry["rarity"]
                ))

                inserted += 1

        db.commit()

        logger.info(
            f"[seed] badges seeded: {inserted} inserted, {updated} updated "
            f"(catalog size: {len(BADGE_CATALOG)})"
        )

    except Exception as exc:

        db.rollback()

        logger.error(f"[seed] seed_badges failed, rolled back: {exc}")

        raise

    return {
        "inserted": inserted,
        "updated": updated,
        "total": len(BADGE_CATALOG)
    }
