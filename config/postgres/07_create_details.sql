CREATE TABLE public.details (
    id BIGSERIAL,
    mileage INT,
    fuel_type VARCHAR(100),
    gearbox_type VARCHAR(100),
    "year" INT        NOT NULL,
    city VARCHAR(255),
    voivodeship VARCHAR(255),
    seller_type VARCHAR(255),
    seller_info TEXT,
    is_featured BOOLEAN,
    is_verified BOOLEAN,
    is_stamped BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT details_pkey PRIMARY KEY (id, "year"),
    CONSTRAINT fk_raw_listing FOREIGN KEY (id) REFERENCES raw_listing(id)
)
PARTITION BY RANGE ("year");

CREATE TABLE public.details_year_lt2000
  PARTITION OF public.details
  FOR VALUES FROM (MINVALUE) TO (2000);

CREATE TABLE public.details_year_2000_2010
  PARTITION OF public.details
  FOR VALUES FROM (2000) TO (2010);

CREATE TABLE public.details_year_2010_2020
  PARTITION OF public.details
  FOR VALUES FROM (2010) TO (2020);

CREATE TABLE public.details_year_2020_2030
  PARTITION OF public.details
  FOR VALUES FROM (2020) TO (2030);

CREATE TABLE public.details_year_gte2030
  PARTITION OF public.details
  FOR VALUES FROM (2030) TO (MAXVALUE);

CREATE INDEX ON public.details_year_lt2000    (mileage);
CREATE INDEX ON public.details_year_2000_2010 (mileage);
CREATE INDEX ON public.details_year_2010_2020 (mileage);
CREATE INDEX ON public.details_year_2020_2030 (mileage);
CREATE INDEX ON public.details_year_gte2030   (mileage);
