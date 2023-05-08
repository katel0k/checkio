-- создаю транзакцию (задание 1). Условия на изоляцию возникли на всякий случай и 
-- из-за того что я буду использовать измненные значения в процессе выполнения транзакции

START TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- задание 7
SAVEPOINT task7;

CREATE PROCEDURE DOWNLOAD()
AS $$
DECLARE table_name text;
BEGIN
    FOR table_name IN (
        SELECT t.table_name FROM information_schema.tables t
        WHERE table_schema LIKE 'public'
    ) LOOP
        EXECUTE format(E'COPY %I TO \'/databases/%I.csv\' DELIMITER \',\' CSV HEADER', table_name, table_name)
            USING table_name;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CALL DOWNLOAD();

-- к сожалению, оказалось, что copy не умеет создавать файлы самостоятельно.
-- Вся эта работа была сделана напрасно и мне пришлось таки создавать файлы вручную:(((((

SAVEPOINT task2;
-- задание 2

UPDATE viewers SET left_dttm = prev_valid_left_dttm - INTERVAL '1 sec'
FROM ( SELECT user_id, 
    lead(joined_dttm, 1, NULL)
    OVER (PARTITION BY user_id ORDER BY joined_dttm) AS prev_valid_left_dttm,
    joined_dttm
FROM viewers ) AS valid
WHERE valid.user_id = viewers.user_id AND 
    valid.joined_dttm = viewers.joined_dttm AND
    viewers.left_dttm IS NULL;

SAVEPOINT task3;
--задание 3

UPDATE rooms SET state='DEAD'
FROM (
    SELECT id, COUNT(viewers.user_id) AS viewer_amount
    FROM rooms LEFT OUTER JOIN viewers ON rooms.id = viewers.room_id 
        AND viewers.left_dttm IS NULL
    GROUP BY rooms.id
) AS valid
WHERE rooms.id = valid.id AND viewer_amount = 0;

SAVEPOINT task4;
-- задание 4

UPDATE games SET outcome='CANCELLED'
FROM (
    SELECT games.id
    FROM (
        SELECT id FROM rooms WHERE state='DEAD'
    ) AS valid JOIN games ON (games.room_id = valid.id)
    WHERE outcome = 'PLAYING'
) AS valid_games
WHERE valid_games.id = games.id;

SAVEPOINT task5;
--задание 5

-- в этой таблице была какая-то неправильная запись, я решил ее убить радикальными методами
TRUNCATE room_history;

-- чтобы не запутываться семантически, я решил переименовать также колонки
ALTER TABLE room_history RENAME COLUMN dttm TO changed_dttm;
ALTER TABLE room_history RENAME COLUMN state TO previous_state;

-- этот запрос скорее всего больше использоваться не будет, поэтому он будет немного более специфичным
-- в том смысле, что я буду использовать то что в данный момент в общем-то все комнаты мертвые

INSERT INTO room_history
    SELECT rooms.id AS room_id, 'WAITING' AS previous_state, MAX(viewers.left_dttm) AS changed_dttm
    FROM rooms LEFT OUTER JOIN viewers ON rooms.id = viewers.room_id
    GROUP BY rooms.id;

-- те комнаты в которых не было пользователей вообще имеют changed_dttm == NULL, это тоже надо исправить

UPDATE room_history SET changed_dttm=NOW()::TIMESTAMP
WHERE changed_dttm IS NULL;

SAVEPOINT task6;
-- задание 6
-- я потратил полтора часа пытаясь установить plpython3u, потому что, оказывается, 
-- у меня не postgres стоящий на alpine, а видимо какой-то свой изолированный образ. Хз как он работает
-- но в итоге я его поставил с помощью банального apt-get install plpython-3-15

CREATE EXTENSION plpython3u;

-- Для конвертацию я импортирую библиотеку из своего проекта, которая уже написана. 
-- Я для этого скопировал прост в / файлик с ней и добавил его для загрузчика

-- imports
DO $$
from sys import path
path.append('/')
import game_logic
import re
GD['game_logic'] = game_logic
GD['re'] = re
GD['game_list'] = {}

def parse(turn_body):
    res = GD['re'].search(r'\((\d), (\d)\) \((\d), (\d)\) (True|False)', turn_body)
    field_from = int(res.group(1)), int(res.group(2))
    field_to = int(res.group(3)), int(res.group(4))
    is_white_player = res.group(5) == 'True'
    return field_from, field_to, is_white_player

GD['parse'] = parse

$$ LANGUAGE plpython3u;

CREATE FUNCTION remake_turn(turn_body text, game_id integer)
    RETURNS text
AS $$

if game_id not in GD['game_list']:
    GD['game_list'][game_id] = GD['game_logic'].Game()

game = GD['game_list'][game_id]

move = GD['game_logic'].GameMove(*GD['parse'](turn_body))
move = game.handle_move(move)

return (f'{move.field_from[0]},{move.field_from[1]},{move.field_to[0]},{move.field_to[1]},'
    + f'{int(move.is_white_player)}{int(move.queens)}{int(move.changes_order)},'
    + (f'{move.eats[0]},{move.eats[1]}' if move.eats else '-'))

$$ LANGUAGE plpython3u;

-- этот запрос обновляет поле body
UPDATE turns SET body=remake_turn(turns.body, turns.game_id);

-- этот запрос обновляет номер хода. Вроде ход должен единственным образом определяться 
-- по времени, пользователю и игре, так что этот код должен быть всегда корректным
UPDATE turns SET index=valid.index
FROM (
    SELECT user_id, game_id, dttm, ROW_NUMBER() OVER (PARTITION BY turns.game_id ORDER BY dttm) AS index
    FROM turns
) AS valid
WHERE turns.user_id=valid.user_id AND turns.game_id=valid.game_id AND turns.dttm=valid.dttm;

SAVEPOINT task8;
-- задание 8

CREATE FUNCTION trigger_insert_room_history()
    RETURNS TRIGGER
AS $$
BEGIN
    INSERT INTO room_history (room_id, previous_state, changed_dttm) VALUES
        (OLD.id, OLD.state, NOW()::TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER room_state_trigger BEFORE UPDATE OF state ON rooms
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_insert_room_history();


-- аналогично измнениям в room_history
ALTER TABLE rating_history RENAME COLUMN dttm TO changed_dttm;
ALTER TABLE rating_history RENAME COLUMN rating TO previous_rating;

CREATE FUNCTION trigger_insert_rating_history()
    RETURNS TRIGGER
AS $$
BEGIN
    INSERT INTO rating_history (user_id, previous_rating, changed_dttm) VALUES
        (OLD.id, OLD.rating, NOW()::TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_rating_trigger BEFORE UPDATE OF rating ON users
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_insert_rating_history();


SAVEPOINT task9;
-- задание 9
ALTER TABLE room_history ALTER COLUMN room_id SET NOT NULL;
ALTER TABLE rating_history ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE turns ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE turns ALTER COLUMN game_id SET NOT NULL;
ALTER TABLE messages ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE messages ALTER COLUMN room_id SET NOT NULL;

ALTER TABLE viewers DROP CONSTRAINT PK_viewers;

SAVEPOINT task10;
-- задание 10
CREATE INDEX user_email_index ON users USING HASH (email);

SAVEPOINT task11;
-- задание 11

-- CREATE VIEW user_info 
-- WITH (
--     SELECT (nickname, user_id, rating) FROM users
-- );

SAVEPOINT task12;
ALTER TABLE games RENAME COLUMN time_start TO started_dttm;
