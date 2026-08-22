-- Convert reward and ticket totals to decimal-capable numeric values.
-- Existing whole numbers are preserved.
ALTER TABLE matches
    ALTER COLUMN home_win_points TYPE NUMERIC(10,2) USING COALESCE(home_win_points, 0)::numeric,
    ALTER COLUMN away_win_points TYPE NUMERIC(10,2) USING COALESCE(away_win_points, 0)::numeric,
    ALTER COLUMN draw_points TYPE NUMERIC(10,2) USING COALESCE(draw_points, 0)::numeric;

ALTER TABLE predictions
    ALTER COLUMN points_won TYPE NUMERIC(10,2) USING COALESCE(points_won, 0)::numeric;

ALTER TABLE prediction_tickets
    ALTER COLUMN possible_points TYPE NUMERIC(10,2) USING COALESCE(possible_points, 0)::numeric,
    ALTER COLUMN points_won TYPE NUMERIC(10,2) USING COALESCE(points_won, 0)::numeric;
