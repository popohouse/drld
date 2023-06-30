-- Adds telegram table
CREATE TABLE IF NOT EXISTS telegram (
    post text PRIMARY KEY
);

UPDATE schema_version set version = 2;