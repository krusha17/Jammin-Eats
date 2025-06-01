-- Migration: tutorial_completion
-- Version: 2
-- Created: 2025-06-01 17:40:00

--UP--
-- Add tutorial_complete column to player_profile
ALTER TABLE player_profile ADD COLUMN tutorial_complete INTEGER DEFAULT 0;

-- Create an index for faster lookups
CREATE INDEX idx_tutorial_complete ON player_profile(tutorial_complete);

--DOWN--
DROP INDEX IF EXISTS idx_tutorial_complete;

-- Remove the tutorial_complete column from player_profile
PRAGMA foreign_keys=off;
BEGIN TRANSACTION;

CREATE TABLE player_profile_backup (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT DEFAULT 'Player',
    high_score INTEGER DEFAULT 0
);

INSERT INTO player_profile_backup SELECT player_id, display_name, high_score FROM player_profile;

DROP TABLE player_profile;

ALTER TABLE player_profile_backup RENAME TO player_profile;

COMMIT;
PRAGMA foreign_keys=on;
