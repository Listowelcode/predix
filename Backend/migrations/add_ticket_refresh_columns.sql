-- Adds the column used to power the daily ticket-refresh cycle.
-- Base.metadata.create_all() only creates NEW tables, so on an
-- existing database this column needs to be added manually.

ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS next_ticket_reset TIMESTAMP NULL;
