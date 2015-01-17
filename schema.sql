CREATE EXTENSION postgis;

DROP TABLE IF EXISTS "user";
CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  email TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_location TIMESTAMP,
  name TEXT NOT NULL,
  password TEXT NOT NULL,
  reset_password_token TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT 't',
  location GEOGRAPHY
);
COMMENT ON COLUMN "user"."email" IS E'email is username';

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
COMMENT ON FUNCTION update_user_table() IS E'When a user\'s location is changed, updated_location is updated and a notification is sent over async message channel with geo data encoded in JSON';

--

CREATE TRIGGER user_update_notify BEFORE UPDATE OR INSERT
    ON "user" FOR EACH ROW EXECUTE PROCEDURE update_user_table();

