-- ==========================================================
-- MANUAL BADGE SEED (fallback)
-- ==========================================================
-- The backend already does this automatically on every startup
-- (see services/seed.py + main.py), so under normal operation
-- you should NOT need to run this by hand.
--
-- Use this only if you want the badges table populated right
-- now, before/without restarting the backend against the new
-- database — e.g. to check things in the Supabase table editor
-- immediately after switching projects.
--
-- Safe to run more than once: it upserts by badge name, so it
-- will never create duplicates.
-- ==========================================================

-- pgcrypto provides gen_random_uuid(); enabled by default on
-- Supabase, this is just a safety net.
create extension if not exists pgcrypto;

-- Adds the rarity column if this badges table pre-dates it.
alter table badges
add column if not exists rarity varchar default 'Common';

insert into badges (id, name, description, icon, rarity)
values
    (gen_random_uuid(), 'First Prediction', 'Make your first prediction.', '🎯', 'Common'),
    (gen_random_uuid(), 'First Win', 'Get your first correct prediction.', '🏆', 'Common'),
    (gen_random_uuid(), 'Hot Streak', 'Win 5 predictions in a row.', '🔥', 'Rare'),
    (gen_random_uuid(), 'Prediction Master', 'Reach 100 correct predictions.', '🧠', 'Epic'),
    (gen_random_uuid(), 'Bronze Predictor', 'Reach the Bronze rank.', '🥉', 'Common'),
    (gen_random_uuid(), 'Silver Predictor', 'Reach the Silver rank.', '🥈', 'Uncommon'),
    (gen_random_uuid(), 'Gold Predictor', 'Reach the Gold rank.', '🥇', 'Rare'),
    (gen_random_uuid(), 'Elite Predictor', 'Reach the Elite rank.', '💎', 'Epic'),
    (gen_random_uuid(), 'Legend', 'Reach 1000 total points.', '👑', 'Legendary')
on conflict (name) do update set
    description = excluded.description,
    icon = excluded.icon,
    rarity = excluded.rarity;
