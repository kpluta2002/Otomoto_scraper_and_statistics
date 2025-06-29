CREATE TABLE IF NOT EXISTS public.car (
    id           BIGSERIAL,
    make         TEXT NOT NULL,
    model        TEXT,
    variant      TEXT,
    engine_cc    NUMERIC,
    power_hp     NUMERIC,
    description  TEXT,
    created_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT car_pkey PRIMARY KEY (id, make)
)PARTITION BY HASH (make);

CREATE TABLE public.car_p0 PARTITION OF public.car
  FOR VALUES WITH (modulus 4, remainder 0);

CREATE TABLE public.car_p1 PARTITION OF public.car
  FOR VALUES WITH (modulus 4, remainder 1);

CREATE TABLE public.car_p2 PARTITION OF public.car
  FOR VALUES WITH (modulus 4, remainder 2);

CREATE TABLE public.car_p3 PARTITION OF public.car
  FOR VALUES WITH (modulus 4, remainder 3);

DO $$
DECLARE
  part TEXT;
BEGIN
  FOREACH part IN ARRAY ARRAY['car_p0','car_p1','car_p2','car_p3'] LOOP
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I_model_idx ON %I (model);', part, part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I_variant_idx ON %I (variant);', part, part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I_engine_cc_idx ON %I (engine_cc);', part, part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I_power_hp_idx ON %I (power_hp);', part, part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I_created_at_idx ON %I (created_at);', part, part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I_updated_at_idx ON %I (updated_at);', part, part);
  END LOOP;
END;
$$ LANGUAGE plpgsql;