CREATE EXTENSION postgis;

DROP TABLE IF EXISTS "user";
CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  location GEOGRAPHY
);

CREATE OR REPLACE FUNCTION update_user_table() RETURNS TRIGGER AS $$
DECLARE
BEGIN
PERFORM pg_notify('user_updated', '{"id": ' 
    || CAST(NEW.id AS text) 
    || ', "location": '
    || ST_AsGeoJSON(NEW.location)
    || '}'
);
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--

DROP TRIGGER IF EXISTS user_update_notify ON "user";
CREATE TRIGGER user_update_notify AFTER UPDATE OR INSERT
    ON "user" FOR EACH ROW EXECUTE PROCEDURE update_user_table();

INSERT INTO "user" (name) VALUES ('danh');
