CREATE EXTENSION postgis;

DROP TABLE IF EXISTS device;
CREATE TABLE device (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  location GEOGRAPHY
);

CREATE OR REPLACE FUNCTION update_device_table() RETURNS TRIGGER AS $$
DECLARE
BEGIN
PERFORM pg_notify('device_updated', '{"id": ' 
    || CAST(NEW.id AS text) 
    || ', "location": '
    || ST_AsGeoJSON(NEW.location)
    || '}'
);
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--

DROP TRIGGER IF EXISTS device_update_notify ON device;
CREATE TRIGGER device_update_notify AFTER UPDATE OR INSERT
    ON device FOR EACH ROW EXECUTE PROCEDURE update_device_table();

INSERT INTO device (name) VALUES ('danh');
