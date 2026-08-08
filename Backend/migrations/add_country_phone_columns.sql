-- Adds the phone number + country columns used to show each player's
-- flag on the leaderboard. Base.metadata.create_all() only creates NEW
-- tables, so on an existing database these columns need to be added
-- manually.

ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS phone VARCHAR NULL;

ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS country VARCHAR(2) NULL;
