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

DROP PROCEDURE IF EXISTS DOWNLOAD();
