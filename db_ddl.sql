START TRANSACTION ISOLATION LEVEL REPEATABLE READ;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nickname VARCHAR(128),
    email VARCHAR(128) UNIQUE NOT NULL,
    password_hash VARCHAR(256),
    rating INTEGER DEFAULT 0
    );

ALTER TABLE users ADD privileges INTEGER DEFAULT 1;

CREATE TYPE room_state AS ENUM ('PLAYING', 'WAITING', 'DEAD');

CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    state room_state DEFAULT 'WAITING',
    creation_dttm TIMESTAMP NOT NULL DEFAULT NOW()::TIMESTAMP
);

CREATE TABLE viewers (
    user_id INTEGER REFERENCES users(id),
    room_id INTEGER REFERENCES rooms(id),
    joined_dttm TIMESTAMP DEFAULT NOW()::TIMESTAMP,
    left_dttm TIMESTAMP
);

ALTER TABLE viewers ADD CONSTRAINT PK_viewers PRIMARY KEY (user_id, room_id);

CREATE TYPE game_outcome AS ENUM ('PLAYING', 'WHITE_WON', 'BLACK_WON', 'DRAW', 'CANCELLED');

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    outcome game_outcome DEFAULT 'PLAYING',
    room_id INTEGER REFERENCES rooms(id),
    time_start TIMESTAMP DEFAULT NOW()::TIMESTAMP
);

CREATE TABLE user_games (
    user_id INTEGER REFERENCES users(id),
    game_id INTEGER REFERENCES games(id),
    is_white BOOLEAN NOT NULL
);

ALTER TABLE user_games ADD CONSTRAINT PK_user_games PRIMARY KEY (user_id, game_id);

CREATE TABLE turns (
    index INTEGER,
    body VARCHAR(32) NOT NULL,
    dttm TIMESTAMP DEFAULT NOW()::TIMESTAMP,
    user_id INTEGER,
    game_id INTEGER
);

ALTER TABLE turns ADD CONSTRAINT FK_turns FOREIGN KEY (user_id, game_id) REFERENCES user_games(user_id, game_id);

CREATE TABLE messages (
    user_id INTEGER,
    room_id INTEGER,
    msg_body VARCHAR(120),
    dttm TIMESTAMP DEFAULT NOW()::TIMESTAMP
);

ALTER TABLE messages ADD CONSTRAINT PK_messages FOREIGN KEY (user_id, room_id) REFERENCES viewers(user_id, room_id);

CREATE TABLE rating_history (
    user_id INTEGER,
    rating INTEGER,
    dttm TIMESTAMP DEFAULT NOW()::TIMESTAMP
);

ALTER TABLE rating_history ADD CONSTRAINT FK_rating FOREIGN KEY (user_id) REFERENCES users(id);

CREATE TABLE room_history (
    room_id INTEGER,
    state room_state,
    dttm TIMESTAMP DEFAULT NOW()::TIMESTAMP
);

ALTER TABLE room_history ADD CONSTRAINT FK_rooms FOREIGN KEY (room_id) REFERENCES rooms(id);

-- добавить update скрипт который будет менять состяние всех стархы комнат 
-- и добавлять время выхода вьюверам оттуда

COMMIT;
