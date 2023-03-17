CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(120),

    );

CREATE TABLE games (
    id SERIAL PRIMARY KEY
    -- player_white INTEGER FOREIGN KEY,
    -- player_black INTEGER FOREIGN KEY,

    );

CREATE TABLE turns (
    game_id INTEGER,
    id INTEGER,
    val CHAR(10),
    CONSTRAINT game_id_key FOREIGN KEY (id) REFERENCES games(id)
    );

CREATE INDEX turn_id_index ON turns(id);

ALTER TABLE turns ADD CONSTRAINT game_turn_id PRIMARY KEY (game_id, id);