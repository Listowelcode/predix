-- Optional over/under market configuration per match.
-- Fixed HOME_WIN / AWAY_WIN / DRAW markets remain in their existing columns.
ALTER TABLE matches
ADD COLUMN IF NOT EXISTS extra_markets JSONB NOT NULL DEFAULT '{}'::jsonb;
