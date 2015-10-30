CREATE EXTENSION postgis;


DROP VIEW IF EXISTS "available_dancars";
DROP TABLE IF EXISTS "user";

CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  mobile TEXT NOT NULL,
  password TEXT NOT NULL,
  reset_password_token TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT 't',
  
  can_pickup BOOLEAN NOT NULL DEFAULT 't',
  pickup_enabled BOOLEAN NOT NULL DEFAULT 'f',
  last_pickup_available_start TIMESTAMP,
  last_pickup_available_duration INTERVAL,
  has_pickup BOOLEAN NOT NULL DEFAULT 'f',

  location GEOGRAPHY,
  updated_location TIMESTAMP,
  location_accuracy_meters NUMERIC
);
COMMENT ON COLUMN "user"."email" IS E'email is username';
COMMENT ON COLUMN "user"."last_pickup_available_start" IS E'last time the user said they were available to pick up a rider';
COMMENT ON COLUMN "user"."last_pickup_available_duration" IS E'how long they are available to give rides. NULL=forever';
COMMENT ON COLUMN "user"."can_pickup" IS E'is capable of giving rides';
COMMENT ON COLUMN "user"."pickup_enabled" IS E'is giving rides right now';
COMMENT ON COLUMN "user"."has_pickup" IS E'currently has a passenger';

-- CREATE FUNCTION user_available_for_pickup(INTEGER) RETURNS BOOL AS $$
-- BEGIN
--   SE

CREATE VIEW "available_dancars" AS
  SELECT * FROM "user" WHERE
    can_pickup='t' AND pickup_enabled='t' AND has_pickup='f' AND last_pickup_available_start IS NOT NULL AND
    (last_pickup_available_duration IS NULL OR ( last_pickup_available_duration IS NOT NULL AND last_pickup_available_start>NOW()-last_pickup_available_duration ));

CREATE TABLE "pickup_request" (
  id SERIAL PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT NOW(),

  requestor_user_id INTEGER NOT NULL REFERENCES "user"(id),
  driver_user_id INTEGER NOT NULL REFERENCES "user"(id),

  accepted BOOLEAN NOT NULL DEFAULT 'f',
  picked_up BOOLEAN NOT NULL DEFAULT 'f',
  completed BOOLEAN NOT NULL DEFAULT 'f',
  cancelled BOOLEAN NOT NULL DEFAULT 'f',

  use_user_location BOOLEAN NOT NULL DEFAULT 't',

  location GEOGRAPHY,
  updated_location TIMESTAMP,
  location_accuracy_meters NUMERIC
);

-- real-time location event spewer
CREATE OR REPLACE FUNCTION update_georeferenced_table() RETURNS TRIGGER AS $$
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
COMMENT ON FUNCTION update_georeferenced_table() IS E'When a table\'s location is changed, updated_location is updated and a notification is sent over async message channel with geo data encoded in JSON';


DROP TRIGGER IF EXISTS "user_update_notify" ON "user";
CREATE TRIGGER user_update_notify BEFORE UPDATE OR INSERT
    ON "user" FOR EACH ROW EXECUTE PROCEDURE update_georeferenced_table();

DROP TRIGGER IF EXISTS "pickup_update_notify" ON "pickup_request";
CREATE TRIGGER pickup_update_notify BEFORE UPDATE OR INSERT
    ON "pickup_request" FOR EACH ROW EXECUTE PROCEDURE update_georeferenced_table();

