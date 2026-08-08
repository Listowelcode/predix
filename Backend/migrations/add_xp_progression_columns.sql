-- Supports the updated XP progression rules (see services/xp.py):
--   * Correct prediction   -> +20 XP (already had an xp column)
--   * Daily login          -> +5 XP  (needs last_login_date)
--   * Matchday completed   -> +15 XP (needs matchday_xp_claims table)
--
-- Base.metadata.create_all() only creates NEW tables, so on an
-- existing database these need to be added manually.

ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS last_login_date DATE NULL;

CREATE TABLE IF NOT EXISTS matchday_xp_claims (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id),
    matchday DATE NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    CONSTRAINT uq_matchday_xp_claims_user_matchday UNIQUE (user_id, matchday)
);
