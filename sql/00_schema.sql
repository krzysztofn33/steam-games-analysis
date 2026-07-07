DROP TABLE IF EXISTS games;

CREATE TABLE games (
    app_id              INTEGER PRIMARY KEY,
    name                TEXT,
    release_date        DATE,
    estimated_owners    TEXT,
    peak_ccu            INTEGER,
    required_age        INTEGER,
    price               NUMERIC(10, 2),
    discount            NUMERIC(10, 2),
    dlc_count           INTEGER,
    about_the_game      TEXT,
    supported_languages TEXT,
    header_image        TEXT,
    windows             BOOLEAN,
    mac                 BOOLEAN,
    linux               BOOLEAN,
    metacritic_score    INTEGER,
    positive            INTEGER,
    negative            INTEGER,
    achievements        INTEGER,
    recommendations     INTEGER,
    average_playtime    INTEGER,
    median_playtime     INTEGER,
    developers          TEXT,
    publishers          TEXT,
    categories          TEXT,
    genres              TEXT,
    tags                TEXT
);

