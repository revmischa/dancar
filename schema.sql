CREATE EXTENSION postgis;

DROP TABLE IF EXISTS "user";
CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_location TIMESTAMP,
  name TEXT NOT NULL,
  location GEOGRAPHY
);

CREATE OR REPLACE FUNCTION update_user_table() RETURNS TRIGGER AS $$
DECLARE
BEGIN
IF ( (TG_OP = 'INSERT' AND NEW.location IS NOT NULL) OR (TG_OP = 'UPDATE' AND NEW.location IS DISTINCT FROM OLD.location) ) THEN
    NEW.updated_location := current_timestamp;
END IF;
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

CREATE TRIGGER user_update_notify BEFORE UPDATE OR INSERT
    ON "user" FOR EACH ROW EXECUTE PROCEDURE update_user_table();

INSERT INTO "user" (name) VALUES ('danh');
